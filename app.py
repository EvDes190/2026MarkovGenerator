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
        "conversion_failed": "文件编码转换失败。"
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
        "conversion_failed": "Сбой преобразования кодировки файла."
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
uploaded_file = st.sidebar.file_uploader(languages[st.session_state.lang]["upload_label"], type=["txt"])

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
    if uploaded_file is not None:
        st.write(languages[st.session_state.lang]["upload_success"])

        # 获取当前脚本所在目录作为项目根目录 / Получение директории скрипта как корня проекта
        base_dir = os.path.dirname(os.path.abspath(__file__))

        #  清空并重建 input/ 目录，写入本次上传的文件
        #    Очистка и пересоздание папки input/, запись загруженного файла
        input_dir = os.path.join(base_dir, "input")
        if os.path.exists(input_dir):
            shutil.rmtree(input_dir)  # 删除旧目录 / Удаление старой папки
        os.makedirs(input_dir)

        # 确保 output/tokenized/ 目录存在（main.exe 运行时需要）
        # Убедиться, что папка output/tokenized/ существует (требуется для main.exe)
        tok_dir = os.path.join(base_dir, "output", "tokenized")
        os.makedirs(tok_dir, exist_ok=True)

        # 预创建 tokenized 文件，防止 main.exe 内 fopen 返回 NULL 导致崩溃
        # Предварительное создание tokenized-файла, чтобы fopen в main.exe не вернул NULL
        input_filename = "uploaded"
        tok_file = os.path.join(tok_dir, f"{input_filename}_tokenized.txt")
        open(tok_file, "w").close()

        # 将上传文件先存到临时目录，再用 recoder.py 转码为 Windows-1251 写入 input/
        # Сохранение загруженного файла во временную папку, затем перекодировка в Windows-1251 и запись в input/
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_path = os.path.join(tmpdir, "raw_upload.txt")       # 原始上传文件 / Исходный загруженный файл
            converted_path = os.path.join(input_dir, f"{input_filename}.txt")  # 转码后文件 / Перекодированный файл

            with open(raw_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 调用 recoder.py 进行编码转换 / Вызов recoder.py для перекодировки
            conversion_success = convert_to_windows1251(raw_path, converted_path, encoding_in=input_encoding)

        if conversion_success:
            st.write(languages[st.session_state.lang]["conversion_success"])
            try:
                main_exe_path = os.path.join(base_dir, "main.exe")

                #  以项目根目录为工作目录运行 main.exe，保证相对路径（input/、output/）正确解析
                #    Запуск main.exe с рабочей директорией проекта для корректного разрешения относительных путей
                process = subprocess.run(
                    [main_exe_path],
                    cwd=base_dir,        # 工作目录 / Рабочая директория
                    capture_output=True,
                    check=True,
                    encoding='windows-1251'
                )

                st.write(languages[st.session_state.lang]["markov_running"])

                #  读取 main.c 固定输出的 output/generated.txt
                #    Чтение файла output/generated.txt, который всегда создаётся main.c
                output_file_path = os.path.join(base_dir, "output", "generated.txt")

                if os.path.exists(output_file_path):
                    with open(output_file_path, "r", encoding='windows-1251', errors='ignore') as f:
                        full_text = f.read()

                    # 按词数截取：main.exe 生成约10万词，这里取前 generation_length 个词
                    # Обрезка по количеству слов: main.exe генерирует ~100000 слов, берём первые generation_length
                    words = full_text.split()
                    generated_text = " ".join(words[:generation_length])

                    # 显示生成结果 / Отображение результата генерации
                    st.subheader(languages[st.session_state.lang]["output_header"])
                    st.text_area(
                        "",
                        generated_text,
                        height=300,
                        key="generated_text_display"
                    )

                    # 提供下载按钮，以 Windows-1251 编码保存 / Кнопка скачивания, сохранение в кодировке Windows-1251
                    st.download_button(
                        label=languages[st.session_state.lang]["save_button"],
                        data=generated_text.encode('windows-1251'),
                        file_name="generated_text.txt",
                        mime="text/plain"
                    )
                else:
                    # output/generated.txt 不存在时报错 / Ошибка, если файл output/generated.txt не найден
                    st.error(languages[st.session_state.lang]["output_file_not_found"])

            except subprocess.CalledProcessError as e:
                # main.exe 返回非零退出码 / main.exe вернул ненулевой код завершения
                st.error(f"{languages[st.session_state.lang]['markov_runtime_error']}{e}")
                st.code(e.stderr)
            except FileNotFoundError:
                # main.exe 文件不存在 / Файл main.exe не найден
                st.error(f"{languages[st.session_state.lang]['main_exe_not_found']}{os.path.dirname(__file__)}{languages[st.session_state.lang]['main_exe_not_found_suffix']}")
            except Exception as e:
                # 其他未知异常 / Прочие неизвестные исключения
                st.error(f"{languages[st.session_state.lang]['unknown_error']}{e}")
        else:
            # 编码转换失败 / Ошибка перекодировки файла
            st.error(languages[st.session_state.lang]["conversion_failed"])
    else:
        # 未上传文件时提示 / Предупреждение, если файл не загружен
        st.warning(languages[st.session_state.lang]["upload_warning"])
