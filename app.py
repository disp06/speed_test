from flask import Flask, request, send_file, jsonify, Response
import os
import io
import socket
import requests
from datetime import datetime
import random
import time

app = Flask(__name__)

# Константы
PORT = 3360
DOWNLOAD_SIZE_MB = 50  # Увеличили размер файла для точности
UPLOAD_TEST_DURATION = 5  # Оптимальная длительность теста
PING_TESTS = 10
PACKET_LOSS_TESTS = 20
CHUNK_SIZE = 1024 * 1024  # 1 МБ чанки для выгрузки

# Функция для получения местоположения клиента по IP
def get_client_location(ip):
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/")
        data = response.json()
        if 'error' not in data:
            return {
                'city': data.get('city', 'Неизвестно'),
                'region': data.get('region', 'Неизвестно'),
                'country': data.get('country_name', 'Неизвестно'),
                'isp': data.get('org', 'Неизвестно')
            }
        return {'city': 'Неизвестно', 'region': 'Неизвестно', 'country': 'Неизвестно', 'isp': 'Неизвестно'}
    except Exception:
        return {'city': 'Неизвестно', 'region': 'Неизвестно', 'country': 'Неизвестно', 'isp': 'Неизвестно'}

# Главная страница
@app.route('/')
def index():
    # HTML код остается без изменений
    return render_index_html()

# Конечная точка для начальной информации
@app.route('/get_info')
def get_info():
    client_ip = request.remote_addr
    location = get_client_location(client_ip)
    return jsonify({
        'client_ip': client_ip,
        'location': location
    })

# Конечная точка для пинга
@app.route('/ping')
def ping():
    return '', 200

# Конечная точка для теста загрузки
@app.route('/download')
def download():
    # Генерируем файл определенного размера
    file_size = DOWNLOAD_SIZE_MB * 1024 * 1024
    return Response(
        generate_random_data(file_size),
        mimetype='application/octet-stream',
        headers={'Content-Length': file_size}
    )

def generate_random_data(size):
    """Генератор случайных данных для экономии памяти"""
    bytes_left = size
    while bytes_left > 0:
        chunk_size = min(bytes_left, CHUNK_SIZE)
        yield os.urandom(chunk_size)
        bytes_left -= chunk_size

# Конечная точка для теста выгрузки
@app.route('/upload', methods=['POST'])
def upload():
    # Просто считаем количество полученных данных
    return '', 200

# Конечная точка для составления отчета
@app.route('/compile_report', methods=['POST'])
def compile_report():
    data = request.json
    client_ip = request.remote_addr
    location = get_client_location(client_ip)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_agent = request.user_agent.string

    report = {
        'client_ip': client_ip,
        'location': location,
        'timestamp': timestamp,
        'dl_speed': data['dlSpeed'],
        'ul_speed': data['ulSpeed'],
        'avg_ping': data['avgPing'],
        'jitter': data['jitter'],
        'packet_loss': data['packetLoss'],
        'user_agent': user_agent
    }
    return jsonify(report)

def render_index_html():
    # HTML код с обновленным JavaScript
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>НЕОНОВЫЙ СКАН СКОРОСТИ</title>
        <style>
            /* Стили остаются без изменений */
        </style>
    </head>
    <body>
        <div class="container">
            <h1>НЕОНОВЫЙ СКАН СКОРОСТИ</h1>
            <p>ЗАПУСТИТЬ ТЕСТ ПОДКЛЮЧЕНИЯ К КИБЕРСЕТИ</p>
            <button onclick="startTest()">АКТИВИРОВАТЬ ПРОТОКОЛ</button>
            <div id="progress"></div>
            <div id="report"></div>
        </div>
        <script>
            async function startTest() {{
                document.getElementById('progress').innerText = 'Инициализация нейронного соединения...';
                let reportDiv = document.getElementById('report');
                reportDiv.innerHTML = '';
                reportDiv.style.display = 'none';

                // Получение IP клиента и другой информации с сервера
                let info = await fetch('/get_info').then(res => res.json());

                // Тест пинга
                document.getElementById('progress').innerText = 'Сканирование узлов задержки...';
                let pings = [];
                for (let i = 0; i < {PING_TESTS}; i++) {{
                    let start = performance.now();
                    await fetch('/ping');
                    let end = performance.now();
                    pings.push(end - start);
                }}
                let avgPing = pings.reduce((a, b) => a + b, 0) / pings.length;
                let jitter = Math.max(...pings) - Math.min(...pings);

                // Тест потерь пакетов
                document.getElementById('progress').innerText = 'Проверка целостности пакетов...';
                let lossCount = 0;
                for (let i = 0; i < {PACKET_LOSS_TESTS}; i++) {{
                    try {{
                        await fetch('/ping', {{ timeout: 1000 }});
                    }} catch {{
                        lossCount++;
                    }}
                }}
                let packetLoss = (lossCount / {PACKET_LOSS_TESTS}) * 100;

                // Тест загрузки
                document.getElementById('progress').innerText = 'Загрузка данных из сети...';
                let dlStart = performance.now();
                const response = await fetch('/download');
                const reader = response.body.getReader();
                let receivedLength = 0;
                
                while(true) {{
                    const {{done, value}} = await reader.read();
                    if (done) break;
                    receivedLength += value.length;
                }}
                
                let dlEnd = performance.now();
                let dlTime = (dlEnd - dlStart) / 1000;
                let dlSpeed = ((receivedLength * 8) / dlTime) / (1024 * 1024); // Мбит/с

                // Тест выгрузки
                document.getElementById('progress').innerText = 'Выгрузка данных в ядро...';
                let uploadData = new ArrayBuffer(1024 * 1024); // 1 МБ
                let ulStart = performance.now();
                let uploadedBytes = 0;
                let testEnd = ulStart + ({UPLOAD_TEST_DURATION} * 1000);
                
                while (performance.now() < testEnd) {{
                    await fetch('/upload', {{
                        method: 'POST',
                        body: uploadData
                    }});
                    uploadedBytes += uploadData.byteLength;
                }}
                
                let ulTime = (performance.now() - ulStart) / 1000;
                let ulSpeed = ((uploadedBytes * 8) / ulTime) / (1024 * 1024); // Мбит/с

                // Формирование отчета
                document.getElementById('progress').innerText = 'Компиляция теневого отчета...';
                let report = await fetch('/compile_report', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        avgPing: avgPing.toFixed(2),
                        jitter: jitter.toFixed(2),
                        packetLoss: packetLoss.toFixed(2),
                        dlSpeed: dlSpeed.toFixed(2),
                        ulSpeed: ulSpeed.toFixed(2)
                    }})
                }}).then(res => res.json());

                // Отображение отчета
                reportDiv.innerHTML = `
                    <div class="report-item"><span class="label">IP КЛИЕНТА:</span> <span class="value">${{report.client_ip}}</span></div>
                    <div class="report-item"><span class="label">МЕСТОПОЛОЖЕНИЕ:</span> <span class="value">${{report.location.city}}, ${{report.location.region}}, ${{report.location.country}} (ISP: ${{report.location.isp}})</span></div>
                    <div class="report-item"><span class="label">ВРЕМЯ:</span> <span class="value">${{report.timestamp}}</span></div>
                    <div class="report-item"><span class="label">СКОРОСТЬ ЗАГРУЗКИ:</span> <span class="value">${{report.dl_speed}} Мбит/с</span></div>
                    <div class="report-item"><span class="label">СКОРОСТЬ ВЫГРУЗКИ:</span> <span class="value">${{report.ul_speed}} Мбит/с</span></div>
                    <div class="report-item"><span class="label">СРЕДНИЙ ПИНГ:</span> <span class="value">${{report.avg_ping}} мс</span></div>
                    <div class="report-item"><span class="label">ДЖИТТЕР:</span> <span class="value">${{report.jitter}} мс</span></div>
                    <div class="report-item"><span class="label">ПОТЕРИ ПАКЕТОВ:</span> <span class="value">${{report.packet_loss}}%</span></div>
                    <div class="report-item"><span class="label">АГЕНТ ПОЛЬЗОВАТЕЛЯ:</span> <span class="value">${{report.user_agent}}</span></div>
                `;
                reportDiv.style.display = 'block';
                document.getElementById('progress').innerText = 'Сканирование завершено. Статус сети: ОНЛАЙН.';
            }}
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, threaded=True)