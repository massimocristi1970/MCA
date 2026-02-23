@echo off
title Business Finance Scorecard App
echo.
echo Starting the Streamlit server for app.py...
echo.

:: Runs the streamlit command
streamlit run app.py

:: If the app stops or fails, the window stays open to show error messages
echo.
echo Streamlit session has ended.
pause