@echo off
rem Motor comun de prueba.bat y completo.bat. No hace falta abrirlo.
setlocal
set "PROYECTO=%~dp0"
for %%I in ("%PROYECTO%..\..") do set "RAIZ=%%~fI"
set "PYTHONPATH=%RAIZ%"

echo ***** Carpeta del proyecto: %RAIZ% *****

set "PYCMD="
if exist "%RAIZ%\.venv\Scripts\python.exe" (
    set "PYCMD="%RAIZ%\.venv\Scripts\python.exe""
) else if exist "%RAIZ%\lib\python\python.exe" (
    set "PYCMD="%RAIZ%\lib\python\python.exe""
) else (
    where uv >nul 2>nul
    if not errorlevel 1 set "PYCMD=uv run python"
)

if not defined PYCMD (
    where python >nul 2>nul
    if not errorlevel 1 set "PYCMD=python"
)

if not defined PYCMD (
    echo.
    echo ***** No encuentro Python. Instala las dependencias primero: *****
    echo *****   uv sync --frozen                                      *****
    echo ***** o usa el paquete de un clic, que ya trae Python dentro.  *****
    echo.
    pause
    exit /b 1
)

pushd "%RAIZ%"
%PYCMD% "%PROYECTO%hacer_video.py" %*
set "CODIGO=%ERRORLEVEL%"
popd

if not "%CODIGO%"=="0" (
    echo.
    echo ***** Ha fallado algo. El motivo esta en los mensajes de arriba. *****
    pause
)
exit /b %CODIGO%
