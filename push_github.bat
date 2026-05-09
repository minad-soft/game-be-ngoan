@echo off
cd /d "%~dp0"

echo ========================================
echo   Day code Game Be Ngoan len GitHub
echo ========================================
echo.

set /p msg="Nhap mo ta thay doi (hoac Enter de dung mac dinh): "
if "%msg%"=="" set msg=Update Game Be Ngoan - %date% %time:~0,5%

echo.
echo [1/3] Them tat ca file...
git add -A

echo [2/3] Commit: %msg%
git commit -m "%msg%"

echo [3/3] Day len GitHub...
git push

echo.
echo ========================================
echo   Da day code len GitHub thanh cong!
echo ========================================
pause
