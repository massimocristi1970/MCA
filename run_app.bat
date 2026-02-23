@echo off
title Business Finance Scorecard App
echo.
echo Activating virtual environment...
call .\.venv\Scripts\activate.bat

echo Starting the Streamlit server for app.py...
echo.

:: Runs the streamlit command using the virtual environment
streamlit run app.py

:: If the app stops or fails, the window stays open to show error messages
echo.
echo Streamlit session has ended.
pause