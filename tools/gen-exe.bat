@echo off
@makensis /V4 /DBitFlag=64bit "%~dp0\installer-proj-win32\cocos.nsi"
@makensis /V4 /DBitFlag=32bit "%~dp0\installer-proj-win32\cocos.nsi"
@"%~dp0\sign-exe.bat"
