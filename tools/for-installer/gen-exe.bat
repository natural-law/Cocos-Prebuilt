@echo off
@iscc /dBitFlag=32bit "%~dp0/installer-proj-win32/Cocos Engine.iss"
@iscc /dBitFlag=64bit "%~dp0/installer-proj-win32/Cocos Engine.iss"
