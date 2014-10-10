; cocos.nsi
;--------------------------------

; define macros
;--------------------------------
!define ROOTPATH ..\..\..
!define PRODUCTNAME cocos
!define JDKInstaller jdk.exe
!define StudioInstaller "CocosStudio.exe"
!define StudioSetupINI "studiosetup.ini"
!define JavaHome "C:\Program Files\Java\jdk1.6.0_45"
!define ToolsDir "$INSTDIR\tools"
!define XDir "$INSTDIR\frameworks\cocos2d-x"
!define RunFirstBat "cocos_runfirst.bat"

!addplugindir ".\resources"

!include "StrFunc.nsh"
!include "MUI.nsh"

; Declare used functions
${StrLoc}

Name "${PRODUCTNAME}"                                            ; The name of the installer
OutFile "${ROOTPATH}\release\${PRODUCTNAME}-${BitFlag}.exe"      ; The file to write

; The default installation directory
!if ${BitFlag} == "64bit"
  InstallDir "$PROGRAMFILES64\${PRODUCTNAME}"
!else
  InstallDir "$PROGRAMFILES32\${PRODUCTNAME}"
!endif

!define StudioDir "$INSTDIR\Cocos Studio"

; The UI related
Icon resources\icon.ico
UninstallIcon resources\icon.ico

!define MUI_ICON "resources\icon.ico"
!define MUI_UNICON "resources\icon.ico"

;--------------------------------
; Pages

  !insertmacro MUI_PAGE_LICENSE "..\resources-common\license.txt"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
 
    # These indented statements modify settings for MUI_PAGE_FINISH
    !define MUI_FINISHPAGE_NOAUTOCLOSE
    !define MUI_FINISHPAGE_RUN
    !define MUI_FINISHPAGE_RUN_TEXT "Start Launcher"
    !define MUI_FINISHPAGE_RUN_FUNCTION "LaunchLink"
  !insertmacro MUI_PAGE_FINISH
 

  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;Languages
!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Functions
Var needAddPath

Function AddPath 
  Var /GLOBAL curPath
  ReadRegStr $curPath HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path"

  Var /GLOBAL findPos
  ${StrLoc} $findPos "$curPath" "$needAddPath" >

  ${If} $findPos != ""
    WriteRegExpandStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path" "$curPath;$needAddPath"
  ${EndIf}
FunctionEnd


;--------------------------------
; The stuff to install
; Section 1
Section "Applications & Framework"

  SectionIn RO

  ; install frameworks
  SetOutPath "$INSTDIR\frameworks"
  File /r /x .DS_Store "${ROOTPATH}\gen\cocos\frameworks\*.*"

  ; install ant
  SetOutPath "${ToolsDir}\ant"
  File /r /x .DS_Store "${ROOTPATH}\gen\cocos\tools\ant\*.*"

  ; install files for windows
  SetOutPath "$INSTDIR"
  File /r /x .DS_Store /x ${JDKINSTALLER} "${ROOTPATH}\gen-win32\${BitFlag}\*.*"

  ; unzip jdk.exe & Cocos Studio.exe into temp directory
  SetOutPath $TEMP
  File "resources\${RunFirstBat}"
  File "${ROOTPATH}\gen-win32\${StudioInstaller}"
  File "${ROOTPATH}\gen-win32\${BitFlag}\${JDKInstaller}"

  ; write ini file for Cocos Studio installing
  ExecWait '"$TEMP\${RunFirstBat}" "$TEMP\${StudioSetupINI}" "$INSTDIR\Cocos Studio"'

  ; install jdk & Cocos Studio
  ExecWait '"$TEMP\${JDKInstaller}" /s'
  ExecWait '"$TEMP\${StudioInstaller}" "/S:$TEMP\${StudioSetupINI}" /NOINIT'

  ; unzip the android SDK & NDK
  ; InitPluginsDir
  ; nsisunz::UnzipToLog "$TEMP\${NDKZipFile}" "${ToolsDir}"

  ; remove temp files
  Delete "$TEMP\${RunFirstBat}"
  Delete "$TEMP\${StudioSetupINI}"
  Delete "$TEMP\${JDKInstaller}"
  Delete "$TEMP\${StudioInstaller}"

  ; Modify Registry
  WriteRegStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "JAVA_HOME" "${JavaHome}"
  StrCpy $needAddPath "${ToolsDir}\Python27"
  Call AddPath
  StrCpy $needAddPath "%JAVA_HOME%\jre\bin"
  Call AddPath
  StrCpy $needAddPath "%JAVA_HOME%\bin"
  Call AddPath

  ; invoke the setup.py
  ExecWait '"${ToolsDir}\Python27\python.exe" "${XDir}\setup.py" -a "" -n "${ToolsDir}\android-ndk-r9d" -t "${ToolsDir}\ant\bin"'

  ; creat desktop icon
  CreateShortCut "$desktop\Cocos Launcher.lnk" "${StudioDir}\CocosStudio.Launcher.exe"
  ; CreateShortCut "$desktop\AnySDK.lnk" "$INSTDIR\AnySDK\bin\AnySDK.exe"
  CreateShortCut "$desktop\Cocos Code IDE.lnk" "$INSTDIR\IDE\Cocos Code IDE.exe"

  WriteUninstaller $INSTDIR\uninstaller.exe
SectionEnd

; Section 2
Section /o "Source Code"

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put file there
  File /r /x .DS_Store "${ROOTPATH}\gen-src\cocos\*.*"
  
SectionEnd

Section "Uninstall"
  ; uninstall Cocos Studio
  ExecWait '"$INSTDIR\Cocos Studio\InstallData\uninstall.exe" "/U:$INSTDIR\Cocos Studio\InstallData\uninstall.xml" /S"'

  ; delete self (see explanation below why this works)
  Delete "$INSTDIR\uninstaller.exe"

  ; delete desktop icon
  ; Delete "$desktop\AnySDK.lnk"
  Delete "$desktop\Cocos Code IDE.lnk"
  Delete "$desktop\Cocos Launcher.lnk"

  RMDir /r /REBOOTOK "$INSTDIR"
SectionEnd

Function LaunchLink
  ExecShell "" "${StudioDir}\CocosStudio.Launcher.exe"
FunctionEnd

