@echo off

set iniFolder=%~dp1
set iniFileName=%~nx1

mkdir "%iniFolder%"

set folder=%2
for /f "useback tokens=*" %%a in ('%folder%') do set folder=%%~a

set folderstr=%%AppFolder%%=%folder%

pushd "%iniFolder%"
echo [SetupValues] > %iniFileName%
echo %folderstr% >> %iniFileName%
popd
