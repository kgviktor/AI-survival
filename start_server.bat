@echo off
chcp 65001 >nul

set "MODEL=%~1"
set "CHAT_MODEL=%~2"

if "%MODEL%"=="" goto help
if "%MODEL%"=="rag" goto rag
if "%MODEL%"=="embedding" goto embedding
if "%MODEL%"=="coder-7b" goto coder7b
if "%MODEL%"=="coder-14b" goto coder14b
if "%MODEL%"=="qwen3-4b" goto qwen34b
if "%MODEL%"=="qwen3-8b" goto qwen38b
if "%MODEL%"=="qwen35-4b" goto qwen354b
if "%MODEL%"=="qwen35-9b" goto qwen359b
goto help

:rag
if "%CHAT_MODEL%"=="" set "CHAT_MODEL=qwen35-4b"
if "%CHAT_MODEL%"=="qwen35-4b" set "CHAT_GGUF=Qwen3.5-4B-Q4_K_M.gguf"
if "%CHAT_MODEL%"=="qwen35-9b" set "CHAT_GGUF=Qwen3.5-9B-Q4_K_M.gguf"
if "%CHAT_MODEL%"=="qwen35-2b" set "CHAT_GGUF=Qwen3.5-2B-Q4_K_M.gguf"
if "%CHAT_MODEL%"=="qwen35-0.8b" set "CHAT_GGUF=Qwen3.5-0.8B-Q8_0.gguf"
if "%CHAT_MODEL%"=="qwen3-4b" set "CHAT_GGUF=Qwen3-4B-Q4_K_M.gguf"
if "%CHAT_MODEL%"=="qwen3-8b" set "CHAT_GGUF=Qwen3-8B-Q4_K_M.gguf"
if "%CHAT_MODEL%"=="qwen3-1.7b" set "CHAT_GGUF=Qwen3-1.7B-Q8_0.gguf"
if "%CHAT_MODEL%"=="qwen3-0.6b" set "CHAT_GGUF=Qwen3-0.6B-Q8_0.gguf"
if not defined CHAT_GGUF goto rag_unknown
echo [*] RAG mode: chat 8080 + embedding 8081
echo [*] Chat: %CHAT_MODEL% - models\%CHAT_GGUF%
echo [*] Embedding:  Qwen3-Embedding-0.6B
echo.
echo [*] Starting embedding server on port 8081...
start "Embedding Server" bin\llama-server.exe -m models\Qwen3-Embedding-0.6B-Q8_0.gguf -t 4 --port 8081 --ctx-size 4096 --embedding
echo [*] Waiting for embedding server to load...
timeout /t 15 /nobreak >nul
echo [*] Starting chat server on port 8080...
bin\llama-server.exe -m models\%CHAT_GGUF% -t 8 --port 8080 --ctx-size 8192
goto end

:rag_unknown
echo [X] Unknown chat model: %CHAT_MODEL%
echo     Available: qwen35-4b qwen35-9b qwen35-2b qwen3-4b qwen3-8b
goto help

:embedding
echo [*] Embedding server only on port 8081...
bin\llama-server.exe -m models\Qwen3-Embedding-0.6B-Q8_0.gguf -t 4 --port 8081 --ctx-size 512 --embedding
goto end

:coder7b
echo [*] Qwen2.5-Coder-7B on port 8080...
bin\llama-server.exe -m models\qwen2.5-coder-7b-instruct-q4_k_m.gguf -t 8 --port 8080 --ctx-size 8192
goto end

:coder14b
echo [*] Qwen2.5-Coder-14B on port 8080...
bin\llama-server.exe -m models\qwen2.5-coder-14b-instruct-q4_k_m.gguf -t 8 --port 8080 --ctx-size 8192
goto end

:qwen34b
echo [*] Qwen3-4B on port 8080...
bin\llama-server.exe -m models\Qwen3-4B-Q4_K_M.gguf -t 8 --port 8080 --ctx-size 8192
goto end

:qwen38b
echo [*] Qwen3-8B on port 8080...
bin\llama-server.exe -m models\Qwen3-8B-Q4_K_M.gguf -t 8 --port 8080 --ctx-size 8192
goto end

:qwen354b
echo [*] Qwen3.5-4B on port 8080...
bin\llama-server.exe -m models\Qwen3.5-4B-Q4_K_M.gguf -t 8 --port 8080 --ctx-size 8192
goto end

:qwen359b
echo [*] Qwen3.5-9B on port 8080...
bin\llama-server.exe -m models\Qwen3.5-9B-Q4_K_M.gguf -t 8 --port 8080 --ctx-size 8192
goto end

:help
echo.
echo  Usage: start_server.bat [model]
echo.
echo  Coding:
echo    coder-7b   - Qwen2.5-Coder 7B  (4.4 GB, ~6 tok/s)
echo    coder-14b  - Qwen2.5-Coder 14B (8.9 GB, ~2.5 tok/s)
echo.
echo  RAG (two servers):
echo    rag              - Embedding + Qwen3.5-4B chat (default)
echo    rag qwen35-9b    - Embedding + Qwen3.5-9B (more capable)
echo    rag qwen3-8b     - Embedding + Qwen3-8B
echo    rag qwen35-2b    - Embedding + Qwen3.5-2B (faster)
echo    embedding        - Embedding model only (8081)
echo.
echo  General:
echo    qwen3-4b   - Qwen3 4B    (2.3 GB, ~10 tok/s)
echo    qwen3-8b   - Qwen3 8B    (4.7 GB, ~6 tok/s)
echo    qwen35-4b  - Qwen3.5 4B  (2.6 GB, ~10 tok/s)
echo    qwen35-9b  - Qwen3.5 9B  (5.3 GB, ~5 tok/s)
echo.
echo  Chat server:  http://localhost:8080
echo  Embed server: http://localhost:8081
echo  Stop with Ctrl+C
echo.

:end
