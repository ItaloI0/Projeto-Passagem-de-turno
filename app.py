from flask import Flask, request, jsonify, send_file, send_from_directory
import weasyprint
from weasyprint import HTML
import os
import tempfile
from datetime import datetime
import base64

app = Flask(__name__)

# Rota principal para servir o formulário HTML
@app.route('/')
def index():
    return send_from_directory('.', 'formulario.html')

def get_base64_image_src(image_path):
    """Converte a imagem em uma string base64 para incorporar no HTML."""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            mime_type = "image/jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
            return f"data:{mime_type};base64,{encoded_string}"
    except FileNotFoundError:
        print(f"Erro: O arquivo de imagem {image_path} não foi encontrado.")
        return ""

# Função principal para gerar o HTML do relatório
def generate_report_html(data):
    base_path = os.path.abspath(os.path.dirname(__file__))
    image_path = os.path.join(base_path, 'Stellantis-Logo2.jpg')
    logo_src = get_base64_image_src(image_path)
    
    # Linha de depuração: Imprime o início da string Base64
    print(f"Início da string Base64 do logo: {logo_src[:50]}...")
    
    data_formatada = data.get('data', '')
    if data_formatada:
        try:
            data_obj = datetime.strptime(data_formatada, '%Y-%m-%d')
            data_formatada = data_obj.strftime('%d/%m/%Y')
        except:
            pass
    equipamentos_html = generate_equipamentos_html(data)
    atividades_html = "<h2>2. ATIVIDADES PROGRAMADAS</h2>"
    atividades_html += generate_activity_html({'ordem': data.get('mecanicaOrdem', []), 'descricao': data.get('mecanicaDescricao', []), 'status': data.get('mecanicaStatus', []), 'observacoes': data.get('mecanicaObservacoes', [])}, '2.1 Mecânica')
    atividades_html += generate_activity_html({'ordem': data.get('eletricaOrdem', []), 'descricao': data.get('eletricaDescricao', []), 'status': data.get('eletricaStatus', []), 'observacoes': data.get('eletricaObservacoes', [])}, '2.2 Elétrica')
    atividades_extras_html = "<h2>3. ATIVIDADES EXTRAS</h2>"
    atividades_extras_html += generate_activity_html({'ordem': data.get('extraOrdem', []), 'descricao': data.get('extraDescricao', []), 'status': data.get('extraStatus', []), 'observacoes': data.get('extraObservacoes', [])}, '')
    observacoes_html = generate_observacoes_html(data.get('observacoes', []))
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Relatório de Passagem de Turno - Energy Center</title>
        <style>
            @page {{ margin: 2cm; size: A4; }}
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #000; background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 50%, #e6f2ff 100%); margin: 0; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #2c5aa0 0%, #4a7bc8 100%); border-radius: 10px; box-shadow: 0 4px 8px rgba(44, 90, 160, 0.2); }}
            .logo {{ max-width: 300px; height: auto; margin-bottom: 20px; }}
            h1 {{ color: #ffffff; margin: 0; font-size: 28px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
            .info-section {{ background: #ffffff; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 5px solid #2c5aa0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .info-section strong {{ color: #2c5aa0; }}
            h2 {{ color: #2c5aa0; border-bottom: 2px solid #4a7bc8; padding-bottom: 10px; margin-top: 30px; font-size: 22px; }}
            h3 {{ color: #2c5aa0; margin-top: 25px; font-size: 18px; }}
            h4 {{ color: #4a7bc8; margin-top: 20px; font-size: 16px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            th {{ background: linear-gradient(135deg, #2c5aa0 0%, #4a7bc8 100%); color: #ffffff; padding: 12px; text-align: left; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.3); }}
            td {{ padding: 10px 12px; border-bottom: 1px solid #e6f2ff; color: #000; }}
            tr:nth-child(even) {{ background: #f8fbff; }}
            tr:hover {{ background: #e6f2ff; }}
            .status-realizada {{ color: #2c5aa0; font-weight: bold; }}
            .status-pendente {{ color: #ff8c00; font-weight: bold; }}
            .status-nao-realizada {{ color: #dc3545; font-weight: bold; }}
            .observacoes {{ background: #f8fbff; padding: 20px; margin: 20px 0; border-radius: 8px; border: 1px solid #e6f2ff; }}
            .observacoes ul {{ margin: 0; padding-left: 20px; }}
            .observacoes li {{ margin: 10px 0; color: #000; }}
            hr {{ border: none; height: 2px; background: linear-gradient(135deg, #2c5aa0 0%, #4a7bc8 100%); margin: 30px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <img src="{logo_src}" class="logo" alt="Logo da Stellantis">
            <h1>RELATÓRIO DE PASSAGEM DE TURNO - ENERGY CENTER</h1>
        </div>
        <div class="info-section">
            <strong>Data:</strong> {data_formatada}<br>
            <strong>Turno:</strong> {data.get('turno', '')}<br>
            <strong>Líder presente:</strong> {data.get('liderPresente', '')}<br>
            <strong>Absenteísmo:</strong> {data.get('absenteismo', '')}<br>
            <strong>Líder próximo turno:</strong> {data.get('liderProximoTurno', '')}
        </div>
        {equipamentos_html}
        {atividades_html}
        {atividades_extras_html}
        {observacoes_html}
    </body>
    </html>
    """
    return html_template

def generate_equipamentos_html(data):
    html = """
    <h2>1. STATUS DOS EQUIPAMENTOS</h2>
    <h3>1.1 Energy Center</h3>
    """
    compressores_map = {
        'energyCompressoresOperacao': 'Em operação',
        'energyCompressoresBackup': 'Backup',
        'energyCompressoresManutencao': 'Em manutenção',
    }
    html += """<h4>Compressores</h4><table><thead><tr><th>Equipamentos</th><th>Status</th><th>Observações</th></tr></thead><tbody>"""
    for key, status in compressores_map.items():
        if data.get(key):
            html += f"""<tr><td>{data.get(key)}</td><td>{status}</td><td>{data.get('energyCompressoresObs', '-')}</td></tr>"""
    if data.get('energyCompressoresSP'):
        html += f"""<tr><td><strong>{data.get('energyCompressoresSP')} Bar</strong></td><td><strong>SP</strong></td><td>-</td></tr>"""
    html += """</tbody></table>"""
    torres_map = {
        'torresOperacao': 'Em operação',
        'torresBackup': 'Backup',
        'torresManutencao': 'Em manutenção'
    }
    html += """<h4>Torres</h4><table><thead><tr><th>Equipamentos</th><th>Status</th><th>Observações</th></tr></thead><tbody>"""
    for key, status in torres_map.items():
        if data.get(key):
            html += f"""<tr><td>{data.get(key)}</td><td>{status}</td><td>{data.get('torresObs', '-')}</td></tr>"""
    html += """</tbody></table>"""
    secadores_map = {
        'energySecadoresOperacao': 'Em operação',
        'energySecadoresBackup': 'Backup',
        'energySecadoresManutencao': 'Em manutenção'
    }
    html += """<h4>Secadores</h4><table><thead><tr><th>Equipamentos</th><th>Status</th><th>Observações</th></tr></thead><tbody>"""
    for key, status in secadores_map.items():
        if data.get(key):
            html += f"""<tr><td>{data.get(key)}</td><td>{status}</td><td>{data.get('energySecadoresObs', '-')}</td></tr>"""
    html += """</tbody></table>"""
    chillers_map = {
        'chillersOperacao': 'Em operação',
        'chillersBackup': 'Backup',
        'chillersManutencao': 'Em manutenção'
    }
    html += """<h4>Chillers</h4><table><thead><tr><th>Equipamentos</th><th>Status</th><th>Observações</th></tr></thead><tbody>"""
    for key, status in chillers_map.items():
        if data.get(key):
            html += f"""<tr><td>{data.get(key)}</td><td>{status}</td><td>{data.get('chillersObs', '-')}</td></tr>"""
    html += """</tbody></table>"""
    bombas_cw_map = {
        'bombasCWOperacao': 'Em operação',
        'bombasCWBackup': 'Backup',
        'bombasCWManutencao': 'Em manutenção'
    }
    html += """<h4>Bombas CW</h4><table><thead><tr><th>Equipamentos</th><th>Status</th><th>Observações</th></tr></thead><tbody>"""
    for key, status in bombas_cw_map.items():
        if data.get(key):
            html += f"""<tr><td>{data.get(key)}</td><td>{status}</td><td>{data.get('bombasCWObs', '-')}</td></tr>"""
    html += """</tbody></table>"""
    bombas_chw_map = {
        'bombasCHWOperacao': 'Em operação',
        'bombasCHWBackup': 'Backup',
        'bombasCHWManutencao': 'Em manutenção'
    }
    html += """<h4>Bombas CHW</h4><table><thead><tr><th>Equipamentos</th><th>Status</th><th>Observações</th></tr></thead><tbody>"""
    for key, status in bombas_chw_map.items():
        if data.get(key):
            html += f"""<tr><td>{data.get(key)}</td><td>{status}</td><td>{data.get('bombasCHWObs', '-')}</td></tr>"""
    html += """</tbody></table>"""
    html += """<h3>1.2 Central de Ar</h3>"""
    central_ar_compressores_map = {
        'centralArCompressoresOperacao': 'Em operação',
        'centralArCompressoresBackup': 'Backup',
        'centralArCompressoresManutencao': 'Em manutenção'
    }
    html += """<h4>Compressores</h4><table><thead><tr><th>Equipamentos</th><th>Status</th><th>Observações</th></tr></thead><tbody>"""
    for key, status in central_ar_compressores_map.items():
        if data.get(key):
            html += f"""<tr><td>{data.get(key)}</td><td>{status}</td><td>{data.get('centralArCompressoresObs', '-')}</td></tr>"""
    html += """</tbody></table>"""
    central_ar_secadores_map = {
        'centralArSecadoresOperacao': 'Em operação',
        'centralArSecadoresEmEspera': 'Em espera',
        'centralArSecadoresManutencao': 'Em manutenção'
    }
    html += """<h4>Secadores</h4><table><thead><tr><th>Equipamentos</th><th>Status</th><th>Observações</th></tr></thead><tbody>"""
    for key, status in central_ar_secadores_map.items():
        if data.get(key):
            html += f"""<tr><td>{data.get(key)}</td><td>{status}</td><td>{data.get('centralArSecadoresObs', '-')}</td></tr>"""
    html += """</tbody></table>"""
    return html

def generate_activity_html(activities, title):
    if not activities.get('ordem'):
        return ""
    html = f"""<h3>{title}</h3><table><thead><tr><th>Ordem</th><th>Descrição</th><th>Status</th><th>Observações</th></tr></thead><tbody>"""
    ordens = activities.get('ordem', [])
    descricoes = activities.get('descricao', [])
    status = activities.get('status', [])
    observacoes = activities.get('observacoes', [])
    for i in range(len(ordens)):
        if ordens[i]:
            status_val = status[i] if i < len(status) else ''
            status_class = ""
            if "Realizada" in status_val:
                status_class = "status-realizada"
            elif "Pendente" in status_val:
                status_class = "status-pendente"
            elif "Não realizada" in status_val:
                status_class = "status-nao-realizada"
            html += f"""
            <tr>
                <td>{ordens[i]}</td>
                <td>{descricoes[i] if i < len(descricoes) else ''}</td>
                <td class="{status_class}">{status_val}</td>
                <td>{observacoes[i] if i < len(observacoes) else '-'}</td>
            </tr>
            """
    html += """</tbody></table>"""
    return html

def generate_observacoes_html(observacoes):
    if not observacoes:
        return ""
    html = """<hr><h2>4. OBSERVAÇÕES IMPORTANTES</h2><div class="observacoes"><ul>"""
    for obs in observacoes:
        html += f"<li>{obs}</li>"
    html += """</ul></div>"""
    return html

@app.route('/gerar-pdf', methods=['POST'])
def gerar_pdf():
    try:
        data = request.get_json()
        html_content = generate_report_html(data)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            html_doc = HTML(string=html_content)
            html_doc.write_pdf(tmp_file.name)
            
            return send_file(
                tmp_file.name,
                as_attachment=True,
                download_name=f"relatorio_passagem_turno_{data.get('data', 'sem_data')}.pdf",
                mimetype='application/pdf'
            )
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)