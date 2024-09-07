from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but they might need fine-tuning.
build_exe_options = {
    "excludes": ["unittest"],
    "includes": ["PySimpleGUI", "selenium", "pytz", "datetime", "json", "time"],
    "bin_includes": ['chromedriver.exe'],
    "zip_include_packages": ["encodings"],
}

setup(
    name="BKCalendar",
    version="0.1",
    description="Bản clone của 1 trường bk nào đó ngoài sg...",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base="gui")],
)