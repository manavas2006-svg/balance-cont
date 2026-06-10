import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from contabilidad.models import Cuenta
from decimal import Decimal

def generar_balance_comprobacion():
    print("\n" + "="*60)
    print("        BALANCE DE COMPROBACIÓN RECURSIVO")
    print("="*60)
    print(f"{'CÓDIGO':<15} | {'NOMBRE DE LA CUENTA':<30} | {'SALDO':>10}")
    print("-"*60)
    cuentas = Cuenta.objects.all()
   
    for cuenta in cuentas:
        saldo = cuenta.obtener_saldo()
        nivel = cuenta.codigo.count('.')
        sangria = "   " * nivel
        nombre_formateado = f"{sangria}{cuenta.nombre}"
        
        print(f"{cuenta.codigo:<15} | {nombre_formateado:<30} | ${saldo:>9.2f}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    generar_balance_comprobacion()