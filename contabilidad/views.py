from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Cuenta, AsientoCabecera, AsientoDetalle

@login_required
def libro_diario_view(request):
    """
    Vista para registrar y listar los asientos contables en el Libro Diario.
    """
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        descripcion = request.POST.get('descripcion')
        
        cuenta_ids = request.POST.getlist('cuenta[]')
        debes = request.POST.getlist('debit[]')
        haberes = request.POST.getlist('credit[]')
        
        total_debe = Decimal('0.00')
        total_haber = Decimal('0.00')
        movimientos_validos = []
        
        for i in range(len(cuenta_ids)):
            if not cuenta_ids[i]: 
                continue
                
            debe_val = Decimal(debes[i]) if debes[i] else Decimal('0.00')
            haber_val = Decimal(haberes[i]) if haberes[i] else Decimal('0.00')
            
            if debe_val > 0 or haber_val > 0:
                total_debe += debe_val
                total_haber += haber_val
                movimientos_validos.append({
                    'cuenta_id': cuenta_ids[i],
                    'debe': debe_val,
                    'haber': haber_val
                })
        
        if not movimientos_validos:
            messages.error(request, "No puedes guardar un asiento vacío sin movimientos.")
            return redirect('libro_diario')
            
        if total_debe != total_haber:
            messages.error(request, f"¡El asiento no cuadra! Debe: ${total_debe} | Haber: ${total_haber}. Diferencia: {abs(total_debe - total_haber)}")
            return redirect('libro_diario')
            
        try:
            with transaction.atomic():
                ultimo_asiento = AsientoCabecera.objects.all().order_by('id').last()
                if ultimo_asiento and ultimo_asiento.codigo.isdigit():
                    nuevo_codigo = str(int(ultimo_asiento.codigo) + 1).zfill(5)
                else:
                    nuevo_codigo = "00001"
                
                asiento = AsientoCabecera.objects.create(
                    codigo=nuevo_codigo,
                    fecha=fecha,
                    descripcion=descripcion
                )
                
                for mov in movimientos_validos:
                    AsientoDetalle.objects.create(
                        asiento=asiento,
                        cuenta_id=mov['cuenta_id'],
                        debe=mov['debe'],
                        haber=mov['haber']
                    )
                    
            messages.success(request, f"¡Asiento Contable Nro. {nuevo_codigo} registrado con éxito!")
        except Exception as e:
            messages.error(request, f"Error crítico en base de datos: {str(e)}")
            
        return redirect('libro_diario')

    
    cuentas_detalle = Cuenta.objects.filter(hijos__isnull=True).order_by('codigo')
    asientos_registrados = AsientoCabecera.objects.all().prefetch_related('detalles__cuenta').order_by('-fecha', '-id')
    
    context = {
        'cuentas': cuentas_detalle,
        'asientos': asientos_registrados
    }
    return render(request, 'contabilidad/diario.html', context)


@login_required
def plan_cuentas_view(request):
    """
    Vista del catálogo de cuentas: maneja la visualización y la creación de nuevas cuentas.
    """
    if request.method == 'POST':
        codigo = request.POST.get('codigo').strip()
        nombre = request.POST.get('nombre').strip()
        tipo = request.POST.get('tipo')
        naturaleza = request.POST.get('naturaleza')
        padre_id = request.POST.get('padre')

        if Cuenta.objects.filter(codigo=codigo).exists():
            messages.error(request, f"¡Error! El código {codigo} ya está registrado en el sistema.")
            return redirect('plan_cuentas')

        try:
            padre = Cuenta.objects.get(id=padre_id) if padre_id else None
            if padre:
                tipo = padre.tipo
                naturaleza = padre.naturaleza

            Cuenta.objects.create(
                codigo=codigo,
                nombre=nombre,
                tipo=tipo,
                naturaleza=naturaleza,
                padre=padre
            )
            messages.success(request, f"Cuenta '{codigo} - {nombre}' añadida con éxito al catálogo.")
        except Exception as e:
            messages.error(request, f"Error al registrar la cuenta: {str(e)}")
            
        return redirect('plan_cuentas')
        
    todas_las_cuentas = Cuenta.objects.all().order_by('codigo')
    
    context = {
        'cuentas_raiz': todas_las_cuentas
    }
    return render(request, 'contabilidad/plan.html', context)


@login_required
def api_balance_comprobacion(request):
    """
    API real que calcula y sirve los saldos acumulados para el Balance de Comprobación.
    """
    cuentas = Cuenta.objects.all().order_by('codigo')
    datos_balance = []
    
    total_debe_general = Decimal('0.00')
    total_haber_general = Decimal('0.00')

    for cuenta in cuentas:
        totales = AsientoDetalle.objects.filter(cuenta=cuenta).aggregate(
            suma_debe=Sum('debe'),
            suma_haber=Sum('haber')
        )
        
        debe = totales['suma_debe'] or Decimal('0.00')
        haber = totales['suma_haber'] or Decimal('0.00')
        
        saldo_deudor = Decimal('0.00')
        saldo_acreedor = Decimal('0.00')
        
        if cuenta.naturaleza == 'DEU':
            saldo_deudor = max(Decimal('0.00'), debe - haber)
        else:
            saldo_acreedor = max(Decimal('0.00'), haber - debe)
            
        total_debe_general += debe
        total_haber_general += haber
        
        if debe > 0 or haber > 0 or not cuenta.hijos.exists():
            datos_balance.append({
                "codigo": cuenta.codigo,
                "nombre": cuenta.nombre,
                "debe": float(debe),
                "haber": float(haber),
                "saldo_deudor": float(saldo_deudor),
                "saldo_acreedor": float(saldo_acreedor),
                "tipo": cuenta.get_tipo_display()
            })

    return JsonResponse({
        "status": "success",
        "totales_generales": {
            "total_debe": float(total_debe_general),
            "total_haber": float(total_haber_general)
        },
        "data": datos_balance
    })