import streamlit as st
import os
import subprocess
import sys
import tempfile
from recoder import convert_to_windows1251 # Assuming recoder.py is in the same directory

# --- 语言选择 / Выбор языка ---
languages = {
    "zh": {"title": "马尔可夫链文本生成器", "upload_label": "上传文本文件", "generate_button": "生成文本", "output_header": "生成结果", "language_select": "选择语言", "generation_length_label": "生成文本长度 (单词)", "upload_success": "文件已上传，开始生成文本...", "generation_placeholder": "文本生成逻辑将在此处实现。", "output_placeholder": "这里将显示生成的文本。", "upload_warning": "请先上传一个文本文件。", "save_button": "保存生成文本", "input_encoding_label": "输入文件编码", "encoding_options": {"utf-8": "UTF-8", "windows-1251": "Windows-1251"}, "conversion_success": "文件编码转换成功，开始调用 Markov 生成器...", "markov_running": "Markov 生成器已运行。", "output_file_not_found": "无法找到生成的文本文件。", "markov_runtime_error": "Markov 生成器运行时出错: ", "main_exe_not_found": "错误: 找不到 main.exe。请确保它位于 '", "main_exe_not_found_suffix": "' 目录中。", "unknown_error": "发生未知错误: ", "conversion_failed": "文件编码转换失败。"},
    "ru": {"title": "Генератор текста цепей Маркова", "upload_label": "Загрузить текстовый файл", "generate_button": "Сгенерировать текст", "output_header": "Сгенерированный текст", "language_select": "Выберите язык", "generation_length_label": "Длина генерируемого текста (слова)", "upload_success": "Файл загружен, начинается генерация текста...", "generation_placeholder": "Логика генерации текста будет реализована здесь.", "output_placeholder": "Здесь будет отображаться сгенерированный текст.", "upload_warning": "Пожалуйста, сначала загрузите текстовый файл.", "save_button": "Сохранить сгенерированный текст", "input_encoding_label": "Кодировка входного файла", "encoding_options": {"utf-8": "UTF-8", "windows-1251": "Windows-1251"}, "conversion_success": "Преобразование кодировки файла успешно, запуск генератора Маркова...", "markov_running": "Генератор Маркова запущен.", "output_file_not_found": "Не удалось найти сгенерированный текстовый файл.", "markov_runtime_error": "Ошибка выполнения генератора Маркова: ", "main_exe_not_found": "Ошибка: main.exe не найден. Убедитесь, что он находится в каталоге '", "main_exe_not_found_suffix": "'.", "unknown_error": "Произошла неизвестная ошибка: ", "conversion_failed": "Сбой преобразования кодировки файла."}
}
if "lang" not in st.session_state:
    st.session_state.lang = "ru" # 默认为俄语 / По умолчанию русский

# 语言选择器 / Выбор языка
st.sidebar.title(languages[st.session_state.lang]["language_select"])
selected_lang = st.sidebar.radio("", options=["ru", "zh"], format_func=lambda x: "Русский" if x == "ru" else "中文")
if selected_lang != st.session_state.lang:
    st.session_state.lang = selected_lang
    st.rerun() # 重新运行以更新语言 / Перезапустить для обновления языка

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
    index=encoding_options_value.index("windows-1251") # 默认为 Windows-1251 / По умолчанию Windows-1251
)
# 从显示名称获取实际编码字符串 / Получить фактическую строку кодировки из отображаемого имени
input_encoding = encoding_options_value[encoding_options_display.index(selected_encoding_display)]

generation_length = st.sidebar.slider(
    languages[st.session_state.lang]["generation_length_label"],
    min_value=10, max_value=1000, value=100, step=10
)

# --- 文本生成按钮 / Кнопка генерации текста ---
if st.button(languages[st.session_state.lang]["generate_button"]):
    if uploaded_file is not None:
        st.write(languages[st.session_state.lang]["upload_success"])

        # 创建一个临时目录 / Создать временный каталог
        with tempfile.TemporaryDirectory() as tmpdir:
            uploaded_file_path = os.path.join(tmpdir, "uploaded_text.txt")
            converted_file_path = os.path.join(tmpdir, "converted_text.txt")
            output_file_path = os.path.join(tmpdir, "generated_output.txt")

            # 保存上传的文件 / Сохранить загруженный файл
            with open(uploaded_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 使用 recoder.py 将文件转换为 windows-1251 编码（根据选择的输入编码） / Преобразовать в windows-1251 с помощью recoder.py с выбранной входной кодировкой
            conversion_success = convert_to_windows1251(uploaded_file_path, converted_file_path, encoding_in=input_encoding)

            if conversion_success:
                st.write(languages[st.session_state.lang]["conversion_success"])
                # 调用 main.exe / Вызвать main.exe
                try:
                    # 构建 main.exe 的命令 / Сформировать команду для main.exe
                    # 确保提供 main.exe 的完整路径 / Убедитесь, что указан полный путь к main.exe
                    main_exe_path = os.path.join(os.path.dirname(__file__), "main.exe")
                    command = [
                        main_exe_path,
                        "-i", converted_file_path,
                        "-o", output_file_path,
                        "-l", str(generation_length)
                    ]
                    
                    process = subprocess.run(command, capture_output=True, text=True, check=True, encoding='windows-1251')
                    
                    st.write(languages[st.session_state.lang]["markov_running"])
                    # 读取生成输出 / Прочитать сгенерированный вывод
                    if os.path.exists(output_file_path):
                        with open(output_file_path, "r", encoding='windows-1251', errors='ignore') as f:
                            generated_text = f.read()
                        
                        st.subheader(languages[st.session_state.lang]["output_header"])
                        st.text_area(
                            "", # 标签为空，因为副标题已提供上下文 / Метка пуста, так как подзаголовок уже предоставляет контекст
                            generated_text,
                            height=300, # 为文本区域设置一个合适的高度 / Установить разумную высоту для текстовой области
                            key="generated_text_display"
                        )
                        st.download_button(
                            label=languages[st.session_state.lang]["save_button"],
                            data=generated_text.encode('windows-1251'), # 编码以匹配原始 C 输出 / Кодировать в соответствии с исходным выводом C
                            file_name="generated_text.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error(languages[st.session_state.lang]["output_file_not_found"])

                except subprocess.CalledProcessError as e:
                    st.error(f"{languages[st.session_state.lang]["markov_runtime_error"]}{e}")
                    st.code(e.stderr)
                except FileNotFoundError:
                    st.error(f"{languages[st.session_state.lang]["main_exe_not_found"]}{os.path.dirname(__file__)}{languages[st.session_state.lang]["main_exe_not_found_suffix"]}")
                except Exception as e:
                    st.error(f"{languages[st.session_state.lang]["unknown_error"]}{e}")
            else:
                st.error(languages[st.session_state.lang]["conversion_failed"])
    else:
        st.warning(languages[st.session_state.lang]["upload_warning"])
