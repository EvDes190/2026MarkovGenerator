import streamlit as st
import os
import subprocess
import sys
import tempfile
import shutil
from recoder import convert_to_windows1251 # Assuming recoder.py is in the same directory

# --- 语言选择 / Выбор языка ---
languages = {
    "zh": {"title": "马尔可夫链文本生成器", "upload_label": "上传文本文件", "generate_button": "生成文本", "output_header": "生成结果", "language_select": "选择语言", "generation_length_label": "生成文本长度 (单词)", "upload_success": "文件已上传，开始生成文本...", "generation_placeholder": "文本生成逻辑将在此处实现。", "output_placeholder": "这里将显示生成的文本。", "upload_warning": "请先上传一个文本文件。", "save_button": "保存生成文本", "input_encoding_label": "输入文件编码", "encoding_options": {"utf-8": "UTF-8", "windows-1251": "Windows-1251"}, "conversion_success": "文件编码转换成功，开始调用 Markov 生成器...", "markov_running": "Markov 生成器已运行。", "output_file_not_found": "无法找到生成的文本文件。", "markov_runtime_error": "Markov 生成器运行时出错: ", "main_exe_not_found": "错误: 找不到 main.exe。请确保它位于 '", "main_exe_not_found_suffix": "' 目录中。", "unknown_error": "发生未知错误: ", "conversion_failed": "文件编码转换失败。"},
    "ru": {"title": "Генератор текста цепей Маркова", "upload_label": "Загрузить текстовый файл", "generate_button": "Сгенерировать текст", "output_header": "Сгенерированный текст", "language_select": "Выберите язык", "generation_length_label": "Длина генерируемого текста (слова)", "upload_success": "Файл загружен, начинается генерация текста...", "generation_placeholder": "Логика генерации текста будет реализована здесь.", "output_placeholder": "Здесь будет отображаться сгенерированный текст.", "upload_warning": "Пожалуйста, сначала загрузите текстовый файл.", "save_button": "Сохранить сгенерированный текст", "input_encoding_label": "Кодировка входного файла", "encoding_options": {"utf-8": "UTF-8", "windows-1251": "Windows-1251"}, "conversion_success": "Преобразование кодировки файла успешно, запуск генератора Маркова...", "markov_running": "Генератор Маркова запущен.", "output_file_not_found": "Не удалось найти сгенерированный текстовый файл.", "markov_runtime_error": "Ошибка выполнения генератора Маркова: ", "main_exe_not_found": "Ошибка: main.exe не найден. Убедитесь, что он находится в каталоге '", "main_exe_not_found_suffix": "'.", "unknown_error": "Произошла неизвестная ошибка: ", "conversion_failed": "Сбой преобразования кодировки файла."}}

if "lang" not in st.session_state:
    st.session_state.lang = "ru" # 默认为俄语 / По умолчанию русский

# 语言选择器 / Выбор языка
st.sidebar.title(languages[st.session_state.lang]["language_select"])
selected_lang = st.sidebar.radio("", options=["ru", "zh"], format_func=lambda x: "Русский" if x == "ru" else "中文")
if selected_lang != st.session_state.lang:
    st.session_state.lang = selected_lang
    st.rerun()

# --- 应用标题 / Заголовок приложения ---
st.title(languages[st.session_state.lang]["title"])

# --- 文件上传器 / Загрузчик файлов ---
uploaded_file = st.sidebar.file_uploader(languages[st.session_state.lang]["upload_label"], type=["txt"])

# 输入编码选择 / Выбор входной кодировки
encoding_options_display = list(languages[st.session_state.lang]["encoding_options"].values())
encoding_options_value = list(languages[st.session_state.lang]["encoding_options"].keys())
selected_encoding_display = st.sidebar.selectbox(
    languages[st.session_state.lang]["input_encoding_label"],
    encoding_options_display,
    index=encoding_options_value.index("windows-1251")
)
input_encoding = encoding_options_value[encoding_options_display.index(selected_encoding_display)]

generation_length = st.sidebar.slider(
    languages[st.session_state.lang]["generation_length_label"],
    min_value=50, max_value=5000, value=500, step=50
)

# --- 文本生成按钮 / Кнопка генерации текста ---
if st.button(languages[st.session_state.lang]["generate_button"]):
    if uploaded_file is not None:
        st.write(languages[st.session_state.lang]["upload_success"])

        base_dir = os.path.dirname(os.path.abspath(__file__))

        # ① 准备 input/ 目录，清空旧文件后写入上传文件
        input_dir = os.path.join(base_dir, "input")
        if os.path.exists(input_dir):
            shutil.rmtree(input_dir)
        os.makedirs(input_dir)

        # 确保 output/ 和 output/tokenized/ 都存在（main.exe 需要这两个目录）
        tok_dir = os.path.join(base_dir, "output", "tokenized")
        os.makedirs(tok_dir, exist_ok=True)

        # 输入文件名固定为 uploaded，提前创建 tokenized 文件（防止 main.exe 的 fopen 返回 NULL 崩溃）
        input_filename = "uploaded"
        tok_file = os.path.join(tok_dir, f"{input_filename}_tokenized.txt")
        open(tok_file, "w").close()  # 预创建空文件

        # 先把原始上传文件保存到临时路径，再转码写入 input/
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_path = os.path.join(tmpdir, "raw_upload.txt")
            converted_path = os.path.join(input_dir, f"{input_filename}.txt")

            with open(raw_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            conversion_success = convert_to_windows1251(raw_path, converted_path, encoding_in=input_encoding)

        if conversion_success:
            st.write(languages[st.session_state.lang]["conversion_success"])
            try:
                main_exe_path = os.path.join(base_dir, "main.exe")

                # ② 以 base_dir 为工作目录运行 main.exe，使相对路径正确
                process = subprocess.run(
                    [main_exe_path],
                    cwd=base_dir,
                    capture_output=True,
                    check=True,
                    encoding='windows-1251'
                )

                st.write(languages[st.session_state.lang]["markov_running"])

                # ③ 读取 main.c 固定写出的 output/generated.txt
                output_file_path = os.path.join(base_dir, "output", "generated.txt")

                if os.path.exists(output_file_path):
                    with open(output_file_path, "r", encoding='windows-1251', errors='ignore') as f:
                        full_text = f.read()

                    # 按词数截取，generation_length 控制输出字数
                    words = full_text.split()
                    generated_text = " ".join(words[:generation_length])

                    st.subheader(languages[st.session_state.lang]["output_header"])
                    st.text_area(
                        "",
                        generated_text,
                        height=300,
                        key="generated_text_display"
                    )
                    st.download_button(
                        label=languages[st.session_state.lang]["save_button"],
                        data=generated_text.encode('windows-1251'),
                        file_name="generated_text.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(languages[st.session_state.lang]["output_file_not_found"])

            except subprocess.CalledProcessError as e:
                st.error(f"{languages[st.session_state.lang]['markov_runtime_error']}{e}")
                st.code(e.stderr)
            except FileNotFoundError:
                st.error(f"{languages[st.session_state.lang]['main_exe_not_found']}{os.path.dirname(__file__)}{languages[st.session_state.lang]['main_exe_not_found_suffix']}")
            except Exception as e:
                st.error(f"{languages[st.session_state.lang]['unknown_error']}{e}")
        else:
            st.error(languages[st.session_state.lang]["conversion_failed"])
    else:
        st.warning(languages[st.session_state.lang]["upload_warning"])
