@echo off

set iniFolder=%~dp1
set iniFileName=%~nx1

mkdir "%iniFolder%"

set folderstr=%%AppFolder%%=%2

pushd "%iniFolder%"
echo [SetupValues] > %iniFileName%
echo %folderstr% >> %iniFileName%
popd
