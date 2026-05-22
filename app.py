import streamlit as st
import os
import subprocess
import tempfile
import shutil
from recoder import convert_to_windows1251  # 从同目录导入编码转换函数 / Импорт функции перекодировки из того же каталога

# --- 界面文本字典（支持中文和俄语）/ Словарь текстов интерфейса (поддержка китайского и русского) ---
languages = {
    "zh": {
        "title": "马尔可夫链文本生成器",
        "upload_label": "上传文本文件",
        "generate_button": "生成文本",
        "output_header": "生成结果",
        "language_select": "选择语言",
        "generation_length_label": "生成文本长度 (单词)",
        "upload_success": "文件已上传，开始生成文本...",
        "generation_placeholder": "文本生成逻辑将在此处实现。",
        "output_placeholder": "这里将显示生成的文本。",
        "upload_warning": "请先上传一个文本文件。",
        "save_button": "保存生成文本",
        "input_encoding_label": "输入文件编码",
        "encoding_options": {"windows-1251": "Windows-1251"},
        "conversion_success": "文件编码转换成功，开始调用 Markov 生成器...",
        "markov_running": "Markov 生成器已运行。",
        "output_file_not_found": "无法找到生成的文本文件。",
        "markov_runtime_error": "Markov 生成器运行时出错: ",
        "main_exe_not_found": "错误: 找不到 main.exe。请确保它位于 '",
        "main_exe_not_found_suffix": "' 目录中。",
        "unknown_error": "发生未知错误: ",
        "conversion_failed": "文件编码转换失败。",
        "processing_file": "正在处理文件: "
    },
    "ru": {
        "title": "Генератор текста цепей Маркова",
        "upload_label": "Загрузить текстовый файл",
        "generate_button": "Сгенерировать текст",
        "output_header": "Сгенерированный текст",
        "language_select": "Выберите язык",
        "generation_length_label": "Длина генерируемого текста (слова)",
        "upload_success": "Файл загружен, начинается генерация текста...",
        "generation_placeholder": "Логика генерации текста будет реализована здесь.",
        "output_placeholder": "Здесь будет отображаться сгенерированный текст.",
        "upload_warning": "Пожалуйста, сначала загрузите текстовый файл.",
        "save_button": "Сохранить сгенерированный текст",
        "input_encoding_label": "Кодировка входного файла",
        "encoding_options": {"windows-1251": "Windows-1251"},
        "conversion_success": "Преобразование кодировки файла успешно, запуск генератора Маркова...",
        "markov_running": "Генератор Маркова запущен.",
        "output_file_not_found": "Не удалось найти сгенерированный текстовый файл.",
        "markov_runtime_error": "Ошибка выполнения генератора Маркова: ",
        "main_exe_not_found": "Ошибка: main.exe не найден. Убедитесь, что он находится в каталоге '",
        "main_exe_not_found_suffix": "'.",
        "unknown_error": "Произошла неизвестная ошибка: ",
        "conversion_failed": "Сбой преобразования кодировки файла.",
        "processing_file": "Обработка файла: "
    }
}

# 初始化语言状态，默认俄语 / Инициализация состояния языка, по умолчанию русский
if "lang" not in st.session_state:
    st.session_state.lang = "ru"

# --- 侧边栏：语言切换 / Боковая панель: переключение языка ---
st.sidebar.title(languages[st.session_state.lang]["language_select"])
selected_lang = st.sidebar.radio(
    "",
    options=["ru", "zh"],
    format_func=lambda x: "Русский" if x == "ru" else "中文"
)
# 切换语言后重新渲染页面 / Перезапуск страницы при смене языка
if selected_lang != st.session_state.lang:
    st.session_state.lang = selected_lang
    st.rerun()

# --- 页面主标题 / Главный заголовок страницы ---
st.title(languages[st.session_state.lang]["title"])

# --- 侧边栏：文件上传控件 / Боковая панель: виджет загрузки файла ---
uploaded_file = st.sidebar.file_uploader(languages[st.session_state.lang]["upload_label"], type=["txt"], accept_multiple_files=False)

# --- 侧边栏：输入文件编码选择 / Боковая панель: выбор кодировки входного файла ---
encoding_options_display = list(languages[st.session_state.lang]["encoding_options"].values())
encoding_options_value = list(languages[st.session_state.lang]["encoding_options"].keys())
selected_encoding_display = st.sidebar.selectbox(
    languages[st.session_state.lang]["input_encoding_label"],
    encoding_options_display,
    index=encoding_options_value.index("windows-1251")  # 默认 Windows-1251 / По умолчанию Windows-1251
)
# 将显示名称映射回实际编码字符串 / Преобразование отображаемого имени в строку кодировки
input_encoding = encoding_options_value[encoding_options_display.index(selected_encoding_display)]

# --- 侧边栏：生成字数滑块（50~5000词）/ Боковая панель: ползунок длины текста (50–5000 слов) ---
generation_length = st.sidebar.slider(
    languages[st.session_state.lang]["generation_length_label"],
    min_value=50, max_value=5000, value=500, step=50
)

# --- 主区域：点击"生成文本"按钮后的处理逻辑 / Основная область: логика обработки после нажатия кнопки ---
if st.button(languages[st.session_state.lang]["generate_button"]):
    # 如果用户上传了文件 / Если пользователь загрузил файлы
    if uploaded_file:
        st.write(languages[st.session_state.lang]["upload_success"])

        base_dir = os.path.dirname(os.path.abspath(__file__))

        # 清空 input/ 目录，为本次所有上传文件做准备 / Очистка папки input/ для всех загруженных файлов
        input_dir = os.path.join(base_dir, "input")
        if os.path.exists(input_dir):
            shutil.rmtree(input_dir)
        os.makedirs(input_dir)

        # 确保 output/tokenized/ 目录存在（main.exe 运行时需要）
        tok_dir = os.path.join(base_dir, "output", "tokenized")
        os.makedirs(tok_dir, exist_ok=True)

        # 获取原始文件名（不含扩展名）和扩展名 / Получить исходное имя файла (без расширения) и расширение
        original_base_name = os.path.splitext(uploaded_file.name)[0]
        original_extension = os.path.splitext(uploaded_file.name)[1]
        st.info(f"{languages[st.session_state.lang]["processing_file"]}{uploaded_file.name}")

        # 将上传文件直接保存到 input/ 目录，保持原始文件名 / Сохранить загруженный файл напрямую в input/, сохраняя исходное имя файла
        with tempfile.TemporaryDirectory() as tmpdir:
            # 构建原始上传文件的临时路径 / Создать временный путь для исходного загруженного файла
            raw_path = os.path.join(tmpdir, uploaded_file.name)
            # 注意：这里直接使用原始文件名保存到 input/ 目录 / Внимание: здесь файл сохраняется в input/ с исходным именем файла
            converted_path_in_input = os.path.join(input_dir, uploaded_file.name)

            # 将上传文件的内容写入临时原始文件 / Записать содержимое загруженного файла во временный исходный файл
            with open(raw_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 调用 recoder.py 进行编码转换并保存到 input/ 目录 / Вызов recoder.py для перекодировки и сохранения в input/
            conversion_success = convert_to_windows1251(raw_path, converted_path_in_input, encoding_in=input_encoding)

            # 如果文件编码转换失败 / Если преобразование кодировки файла не удалось
            if not conversion_success:
                st.error(f"{languages[st.session_state.lang]["conversion_failed"]} (File: {uploaded_file.name})")
            else: # Only run main.exe if conversion was successful
                # 预创建 tokenized 文件，防止 main.exe 内 fopen 返回 NULL 导致崩溃 (此步骤移至此处，只执行一次)
                # Предварительное создание tokenized-файла, чтобы fopen в main.exe не вернул NULL (этот шаг перемещен сюда, выполняется один раз)
                input_filename_for_exe_placeholder = "uploaded" # 假设 main.exe 仍然会查找这个占位文件 / Предполагается, что main.exe все еще будет искать этот файл-заполнитель
                tok_file_for_exe = os.path.join(tok_dir, f"{input_filename_for_exe_placeholder}_tokenized.txt")
                open(tok_file_for_exe, "w").close()  # 预创建空文件 / Предварительное создание пустого файла

                try:
                    main_exe_path = os.path.join(base_dir, "main.exe")

                    # 以 base_dir 为工作目录运行 main.exe，保证相对路径正确
                    # Запуск main.exe с рабочей директорией base_dir для корректного разрешения относительных путей
                    process = subprocess.run(
                        [main_exe_path],
                        cwd=base_dir,
                        capture_output=True,
                        check=True,
                        encoding='windows-1251'
                    )

                    st.write(languages[st.session_state.lang]["markov_running"])

                    # 读取 main.exe 固定写出的 output/generated.txt (假设这是所有输入的总结果)
                    # Чтение файла output/generated.txt, который всегда создаётся main.exe (предполагается, что это общий результат всех входных данных)
                    output_file_path_from_exe = os.path.join(base_dir, "output", "generated.txt")

                    # 检查生成的总结果文件是否存在 / Проверить, существует ли общий файл результатов
                    if os.path.exists(output_file_path_from_exe):
                        # 以 Windows-1251 编码读取生成的文本 / Считать сгенерированный текст в кодировке Windows-1251
                        with open(output_file_path_from_exe, "r", encoding='windows-1251', errors='ignore') as f:
                            full_text = f.read()

                        # 按词数截取：main.exe 生成约10万词，这里取前 generation_length 个词 / Обрезка по количеству слов: main.exe генерирует ~100000 слов, берём первые generation_length
                        words = full_text.split()
                        generated_text = " ".join(words[:generation_length])

                        # 显示生成结果的标题 / Заголовок для отображения результатов генерации
                        st.subheader(languages[st.session_state.lang]["output_header"])
                        st.text_area(
                            "Результат генерации для всех файлов",
                            generated_text,
                            height=300,
                            key="generated_text_display_all"
                        )

                        # 提供下载按钮，以 Windows-1251 编码保存 / Кнопка скачивания, сохранение в кодировке Windows-1251
                        st.download_button(
                            label=languages[st.session_state.lang]["save_button"],
                            data=generated_text.encode('windows-1251'),
                            file_name="all_generated_text.txt",
                            mime="text/plain",
                            key="download_button_all"
                        )
                        # 清理 generated.txt，确保下次运行时是新的结果 / Очистка generated.txt, чтобы при следующем запуске был новый результат
                        os.remove(output_file_path_from_exe)

                    else:
                        # 如果生成文件未找到，则显示错误信息 / Если сгенерированный файл не найден, отобразить сообщение об ошибке
                        st.error(languages[st.session_state.lang]["output_file_not_found"])

                except subprocess.CalledProcessError as e:
                    # main.exe 返回非零退出码，表示运行出错 / main.exe вернул ненулевой код завершения, указывая на ошибку выполнения
                    st.error(f"{languages[st.session_state.lang]['markov_runtime_error']}{e}")
                    st.code(e.stderr)
                except FileNotFoundError:
                    # main.exe 文件不存在 / Файл main.exe 不存在
                    st.error(f"{languages[st.session_state.lang]['main_exe_not_found']}{os.path.dirname(__file__)}{languages[st.session_state.lang]['main_exe_not_found_suffix']}")
                except Exception as e:
                    # 捕获其他未知异常 / Перехват других未知异常
                    st.error(f"{languages[st.session_state.lang]['unknown_error']}{e}")
    else:
        # 如果没有上传文件，则显示警告信息 / Предупреждение, если файл не загружен
        st.warning(languages[st.session_state.lang]["upload_warning"])
