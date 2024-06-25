pyinstaller ^
    --noconfirm ^
    --console ^
    --recursive-copy-metadata "openai-whisper" ^
    --hidden-import=tiktoken_ext.openai_public ^
    --hidden-import=tiktoken_ext ^
    --collect-data sv_ttk ^
    --add-data "resources/images/icon.ico;resources/images/" ^
    --add-data "venv/Lib/site-packages/whisper/assets/;whisper/assets/" ^
    --name "MagicSpeech" ^
    --onefile ^
    --icon "resources/images/icon.ico" ^
    --splash "resources/images/icon.ico" ^
    ui.py