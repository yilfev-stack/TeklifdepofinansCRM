@echo off
setlocal

REM === DEMART TEKLIF PROGRAMI BASLATMA ===

echo ============================================
echo        TEKLIF PROGRAMI BASLATILIYOR
echo ============================================
echo.

REM 1) Script klasorune git
cd /d "%~dp0"

REM 2) Docker daemon hazir mi kontrol et
echo Docker durumu kontrol ediliyor...
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker calismiyor, Docker Desktop aciliyor...
    if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    ) else (
        echo [UYARI] Docker Desktop.exe bulunamadi. Yine de denenecek...
    )

    echo Docker'in hazir olmasi bekleniyor...
    for /L %%i in (1,1,20) do (
        timeout /t 3 >nul
        docker info >nul 2>&1
        if not errorlevel 1 (
            goto :docker_ready
        )
        echo  - Deneme %%i: Docker henuz hazir degil...
    )

    echo.
    echo [HATA] Docker daemon'a erisilemiyor. Lütfen Docker Desktop'i manuel acin.
    echo.
    pause
    exit /b 1
)

:docker_ready
echo Docker hazir.
echo.

REM 3) Container'lari build edip calistir
echo Container'lar build edilip calistiriliyor...
docker-compose up -d --build

echo.
echo Container'lar hazirlaniyor...
timeout /t 3 >nul

REM 4) Tarayiciyi ac
echo Tarayici aciliyor: http://localhost:3001
start "" "http://localhost:3001"

echo.
echo ============================================
echo     TEKLIF PROGRAMI CALISIYOR
echo ============================================
echo.
pause

endlocal
