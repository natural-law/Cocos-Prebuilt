@echo off
@iscc /dBitFlag=64bit "%~dp0/installer-proj-win32/Cocos Creator.iss"
@iscc /dBitFlag=32bit "%~dp0/installer-proj-win32/Cocos Creator.iss"
