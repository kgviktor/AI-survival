@echo off
chcp 65001 >nul

:: ===================================================
::  AI Survival - Quick launch
::  Usage: run.bat <model>
::  Example: run.bat qwen3.5-4b
:: ===================================================

set MODEL=%1

if "%MODEL%"=="qwen3.5-0.8b" (
    bin\llama-cli.exe -m models\Qwen3.5-0.8B-Q8_0.gguf -t 8 -cnv
) else if "%MODEL%"=="qwen3.5-2b" (
    bin\llama-cli.exe -m models\Qwen3.5-2B-Q4_K_M.gguf -t 8 -cnv
) else if "%MODEL%"=="qwen3.5-4b" (
    bin\llama-cli.exe -m models\Qwen3.5-4B-Q4_K_M.gguf -t 8 -cnv
) else if "%MODEL%"=="qwen3.5-9b" (
    bin\llama-cli.exe -m models\Qwen3.5-9B-Q4_K_M.gguf -t 8 -cnv
) else if "%MODEL%"=="qwen3-4b" (
    bin\llama-cli.exe -m models\Qwen3-4B-Q4_K_M.gguf -t 8 -cnv
) else if "%MODEL%"=="qwen3-8b" (
    bin\llama-cli.exe -m models\Qwen3-8B-Q4_K_M.gguf -t 8 -cnv
) else if "%MODEL%"=="qwen3-14b" (
    bin\llama-cli.exe -m models\Qwen3-14B-Q4_K_M.gguf -t 8 -cnv
) else if "%MODEL%"=="qwen3-0.6b" (
    bin\llama-cli.exe -m models\Qwen3-0.6B-Q8_0.gguf -t 8 -cnv
) else if "%MODEL%"=="qwen3-1.7b" (
    bin\llama-cli.exe -m models\Qwen3-1.7B-Q8_0.gguf -t 8 -cnv
) else if "%MODEL%"=="coder-7b" (
    bin\llama-cli.exe -m models\qwen2.5-coder-7b-instruct-q4_k_m.gguf -t 8 -cnv
) else if "%MODEL%"=="coder-14b" (
    bin\llama-cli.exe -m models\qwen2.5-coder-14b-instruct-q4_k_m.gguf -t 8 -cnv
) else (
    echo.
    echo  Usage: run.bat ^<model^>
    echo.
    echo  Available models:
    echo    qwen3.5-0.8b -- Qwen3.5 0.8B (ultra fast)
    echo    qwen3.5-2b   -- Qwen3.5 2B (light)
    echo    qwen3.5-4b   -- Qwen3.5 4B (fast)
    echo    qwen3.5-9b   -- Qwen3.5 9B (capable)
    echo    qwen3-0.6b   -- Qwen3 0.6B (ultra fast)
    echo    qwen3-1.7b   -- Qwen3 1.7B
    echo    qwen3-4b     -- Qwen3 4B
    echo    qwen3-8b     -- Qwen3 8B
    echo    qwen3-14b    -- Qwen3 14B
    echo    coder-7b     -- Qwen2.5-Coder 7B
    echo    coder-14b    -- Qwen2.5-Coder 14B
    echo.
)
