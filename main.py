from flask import Flask, render_template, request, jsonify
# основная среда для веб-приложений
# отображает HTML-шаблоны.
# обрабатывает входящие запросы.
# преобразует данные в формат JSON для ответов.
from flask import send_from_directory
# отправляет файлы из указанного каталога.
from werkzeug.utils import secure_filename
# очищает имена файлов, чтобы гарантировать их безопасное использование
import os
# взаимодействует с операционной системой для операций с файлами и каталогами

from mod.txt_processor import process_txt_file
from mod.xml_processor import process_xml_file
from mod.json_processor import process_json_file
from mod.yaml_processor import process_yaml_file

app = Flask(__name__)

# определяем каталоги для загружаемых файлов и обработанных выходных данных
UPLOAD_FOLDER = 'data'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# jпределяеv маршрут для загрузки обработанных файлов
@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# Главная страница с формой
@app.route('/')
def index():
    return render_template('index.html')

# Обработка файла
@app.route('/process', methods=['POST'])
def process_file():
    try:
        uploaded_file = request.files['file']
        method = int(request.form['method'])

        if uploaded_file.filename == '':
            return jsonify({'status': 'error', 'message': 'Файл не выбран.'})

        filename = secure_filename(uploaded_file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, f"processed_{filename}")
        uploaded_file.save(input_path)

        file_type = filename.rsplit('.', 1)[-1].lower()

        # Определяем обработку
        if file_type == 'txt':
            process_txt_file(input_path, output_path, method)
        elif file_type == 'xml':
            process_xml_file(input_path, output_path, method)
        elif file_type == 'json':
            process_json_file(input_path, output_path, method)
        elif file_type == 'yaml':
            process_yaml_file(input_path, output_path, method)
        else:
            return jsonify({'status': 'error', 'message': 'Неподдерживаемый тип файла.'})

        return jsonify({'status': 'success', 'message': f'Файл успешно обработан.', 'download_url': f'/download/{os.path.basename(output_path)}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Запускает приложение Flask в режиме отладки, который
# выводит подробные сообщения об ошибках и автоматически
# перезагружает сервер при изменении кода
if __name__ == '__main__':
    app.run(debug=True)