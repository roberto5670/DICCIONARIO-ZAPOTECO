@echo off
setlocal

title Compilar Aplicacion

echo ============================================
echo      COMPILANDO APLICACION
echo ============================================
echo.

:: Cambiar al directorio donde está este .bat
cd /d "%~dp0"

:: Eliminar compilaciones anteriores
if exist build (
    echo Eliminando carpeta build...
    rmdir /s /q build
)

if exist dist (
    echo Eliminando carpeta dist...
    rmdir /s /q dist
)

if exist app.spec (
    echo Eliminando app.spec...
    del /f /q app.spec
)

echo.
echo Iniciando compilacion...
echo.

python -m PyInstaller ^
--noconfirm ^
--clean ^
--onedir ^
--windowed ^
--icon=icono.ico ^
--add-data "templates;templates" ^
--add-data "static;static" ^
--add-data "diccionario_zapoteco.db;." ^
app.py

echo.
echo ============================================
echo.

if exist "dist\app\app.exe" (
    echo COMPILACION EXITOSA
    echo.
    echo Ejecutable creado en:
    echo %CD%\dist\app\
    echo.
    start "" "dist\app"
) else (
    echo ERROR: No se pudo generar el ejecutable.
)

echo.
pause