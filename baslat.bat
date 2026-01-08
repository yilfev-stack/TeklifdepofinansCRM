@echo off
echo Uygulama baslatiliyor...
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo.
echo Uygulama baslatildi!
echo Frontend: http://localhost:3001
echo Backend: http://localhost:8001
pause
