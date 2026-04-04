@echo off
cd /d "%~dp0"
echo ================================================
echo   HDRnote - 洗腎室病患系統
echo ================================================
echo.

REM 載入密碼
call secrets.bat

REM 啟動 server（掛掉自動重啟的迴圈）
echo [1/2] 啟動本地伺服器...
start "HDRnote Server" cmd /c ":loop & python server.py & echo [HDRnote] Server 重啟中... & timeout /t 3 /nobreak >nul & goto loop"

timeout /t 2 /nobreak >nul

REM 啟動 Cloudflare Tunnel
echo [2/2] 啟動 Cloudflare Tunnel...
echo.
echo 請複製下方網址傳給手機使用
echo ================================================
cloudflared tunnel --url http://localhost:8080
