@echo off
@CSignTool sign /r "Cocos Installer" /f "%~dp0\..\release\Cocos-64bit.exe"
@CSignTool sign /r "Cocos Installer" /f "%~dp0\..\release\Cocos-32bit.exe"
