' This script runs the Python tray application in the background without a visible console window.

' Replace with the full path to your Python executable
Dim pythonExePath
pythonExePath = "C:\\Users\\natha\\AppData\\Local\\Programs\\Python\\Python313\\pythonw.exe"

' Replace with the full path to your Python script
Dim scriptPath
scriptPath = "c:\\Users\\natha\\Documents\\Scripts\\main.py"

' Create a shell object
Set WshShell = CreateObject("WScript.Shell")

' Run the Python script using pythonw.exe (which does not open a console window)
' The "0" at the end of .Run specifies a hidden window.
WshShell.Run """" & pythonExePath & """ """ & scriptPath & """", 0, False

Set WshShell = Nothing