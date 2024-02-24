set pythonpath=venv\Lib\site-packages;sign
nuitka --windows-icon-from-ico=jd.ico  --follow-imports  --include-data-files=config-test.ini=. --plugin-enable=upx --upx-binary=D:/tools/upx-4.2.1-win64/upx.exe --remove-output --standalone --show-progress --output-filename=jd-seckll --output-dir=out main.py
