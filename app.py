from flask import Flask, request, render_template, flash
import ipaddress

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_flask'

def calcular_ip(ip_address, mask):
    try:
        mask = int(mask)
        network = ipaddress.IPv4Network(f"{ip_address}/{mask}", strict=False)
        
        ip_red = network.network_address
        ip_broadcast = network.broadcast_address
        cantidad_hosts = network.num_addresses - 2
        rango_ips = list(network.hosts())
        clase_ip = calcular_clase(ip_address)
        ip_publica_privada = 'Privada' if network.is_private else 'Pública'
        binario_red_host = obtener_binario(ip_address, mask)

        return {
            "ip_red": ip_red,
            "ip_broadcast": ip_broadcast,
            "cantidad_hosts": cantidad_hosts,
            "rango_ips": f"{rango_ips[0]} - {rango_ips[-1]}",
            "clase_ip": clase_ip,
            "ip_publica_privada": ip_publica_privada,
            "binario_red_host": binario_red_host
        }
    except ipaddress.AddressValueError:
        flash("La IP ingresada no es válida. Por favor, ingresa una IP correcta.")
        return None
    except ipaddress.NetmaskValueError:
        flash("La máscara de subred ingresada no es válida. Por favor, ingresa una máscara correcta.")
        return None
    except ValueError:
        flash("La IP o máscara ingresada no es válida. Por favor, verifica los datos.")
        return None

def calcular_clase(ip_address):
    primer_octeto = int(ip_address.split('.')[0])
    if 1 <= primer_octeto <= 126:
        return 'A'
    elif 128 <= primer_octeto <= 191:
        return 'B'
    elif 192 <= primer_octeto <= 223:
        return 'C'
    elif 224 <= primer_octeto <= 239:
        return 'D (Multicast)'
    else:
        return 'E (Experimental)'

def obtener_binario(ip_address, mask):
    ip_binario = ''.join([f'{int(octeto):08b}' for octeto in ip_address.split('.')])
    
    bits_red = min(mask, 8)
    bits_subred = min(max(mask - bits_red, 0), 8)
    bits_host = max(32 - bits_red - bits_subred, 0)

    red = ip_binario[:bits_red].ljust(8, '0')
    subred = ip_binario[bits_red:bits_red + bits_subred].ljust(8, '0')
    host = ip_binario[bits_red + bits_subred:].ljust(8, '0')
    
    ip_binario_completo = red + subred + host
    
    octetos = [ip_binario_completo[i:i + 8] for i in range(0, 32, 8)]
    
    red_html = f"<span class='red'>{octetos[0]}</span>"
    subred_html = f"<span class='subred'>{octetos[1]}</span>" if mask > 8 else ''
    host_html = f"<span class='host'>{'.'.join(octetos[2:])}</span>" if mask > 16 else f"<span class='host'>{octetos[1]}</span>"
    
    resultado_binario = f"{red_html}.{subred_html}.{host_html}".replace('..', '.').strip('.')
    
    return resultado_binario

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    if request.method == 'POST':
        ip = request.form['ip']
        mascara = request.form['mask']
        try:
            mascara = int(mascara)
            if mascara < 0 or mascara > 32:
                raise ValueError("Máscara fuera del rango válido.")
        except ValueError:
            flash("Por favor, ingresa un valor numérico válido para la máscara de subred (0-32).")
            return render_template('index.html', resultado=None)
        
        resultado = calcular_ip(ip, mascara)
    return render_template('index.html', resultado=resultado)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
