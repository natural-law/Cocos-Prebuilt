; cocos.nsi
;--------------------------------

; define macros
;--------------------------------
!define ROOTPATH ..\..
!define PRODUCTNAME Cocos
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
!include nsDialogs.nsh
!include "resources\SamplesDir.nsdinc"

!include WinVer.nsh
!include x64.nsh

!include "resources\EnvVarUpdate.nsh"

; Declare used functions
${StrLoc}

Name "${PRODUCTNAME}"                                            ; The name of the installer
OutFile "${ROOTPATH}\release\${PRODUCTNAME}-${BitFlag}.exe"      ; The file to write

BrandingText "Cocos Installer"

; The default installation directory
; !if ${BitFlag} == "64bit"
;   InstallDir "$PROGRAMFILES64\${PRODUCTNAME}"
; !else
;   InstallDir "$PROGRAMFILES32\${PRODUCTNAME}"
; !endif

InstallDir "C:\Cocos"
!define RegView 32

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

  !define MUI_PAGE_CUSTOMFUNCTION_LEAVE dir_leave
  !insertmacro MUI_PAGE_DIRECTORY
  Page Custom fnc_SamplesDir_Show fnc_SamplesDir_Leave
  !insertmacro MUI_PAGE_INSTFILES
 
    # These indented statements modify settings for MUI_PAGE_FINISH
    !define MUI_FINISHPAGE_NOAUTOCLOSE
    # !define MUI_FINISHPAGE_RUN
    # !define MUI_FINISHPAGE_RUN_TEXT "Start ${PRODUCTNAME}"
    # !define MUI_FINISHPAGE_RUN_FUNCTION "LaunchLink"
  !insertmacro MUI_PAGE_FINISH
 

  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;Languages
!insertmacro MUI_LANGUAGE "English"

Var samplesDir

;--------------------------------
; The stuff to install
; Section 1
SectionGroup "Frameworks" SectionFramework

Section "Prebuilt libs" SectionPrebuilt

  SectionIn RO

  ; install frameworks
  SetOutPath "$INSTDIR\frameworks"
  File /r /x .DS_Store "${ROOTPATH}\gen\${PRODUCTNAME}\frameworks\*.*"

  ; install templates
  SetOutPath "$INSTDIR\templates"
  File /r /x .DS_Store "${ROOTPATH}\gen\${PRODUCTNAME}\templates\*.*"

SectionEnd

Section /o "Source Code" SectionSource

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put file there
  File /r /x .DS_Store "${ROOTPATH}\gen-src\${PRODUCTNAME}\*.*"
  
SectionEnd

SectionGroupEnd

; Section 2
Section "Tools" SectionTools

  SectionIn RO

  ; install ant
  SetOutPath "${ToolsDir}\ant"
  File /r /x .DS_Store "${ROOTPATH}\gen\${PRODUCTNAME}\tools\ant\*.*"

  ; install files for windows
  SetOutPath "$INSTDIR"
  File /r /x .DS_Store /x ${JDKINSTALLER} "${ROOTPATH}\gen-win32\${BitFlag}\*.*"

  ; Write install path into registry
  SetRegView ${RegView}
  WriteRegStr HKLM "Software\Cocos" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "Software\Cocos" "CocosCodeIDEDir" "$INSTDIR\IDE"

  ; unzip jdk.exe & Cocos Studio.exe into temp directory
  SetOutPath $TEMP
  File "resources\${RunFirstBat}"
  File "${ROOTPATH}\gen-win32\${StudioInstaller}"
  File "${ROOTPATH}\gen-win32\${BitFlag}\${JDKInstaller}"

  ; write ini file for Cocos Studio installing
  ExecWait '"$TEMP\${RunFirstBat}" "$TEMP\${StudioSetupINI}" "$INSTDIR\Cocos Studio"'

  ; install jdk & Cocos Studio
  ExecWait '"$TEMP\${JDKInstaller}" /s'
  ExecWait '"$TEMP\${StudioInstaller}" "/S:$TEMP\${StudioSetupINI}" /Doc "$samplesDir" /NoRestart /NOINIT'

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

  ${EnvVarUpdate} $0 "PATH" "A" "HKCU" "${ToolsDir}\Python27"
  ${EnvVarUpdate} $0 "PATH" "A" "HKCU" "%JAVA_HOME%\jre\bin"
  ${EnvVarUpdate} $0 "PATH" "A" "HKCU" "%JAVA_HOME%\bin"

  ; invoke the setup.py
  ExecWait '"${ToolsDir}\Python27\python.exe" "${XDir}\setup.py" -a "" -n "${ToolsDir}\android-ndk-r9d" -t "${ToolsDir}\ant\bin"'

  ; creat desktop icon
  ; CreateShortCut "$desktop\${PRODUCTNAME}.lnk" "${StudioDir}\CocosStudio.Launcher.exe"
  ; CreateShortCut "$desktop\AnySDK.lnk" "$INSTDIR\AnySDK\bin\AnySDK.exe"
  CreateShortCut "$desktop\Cocos Code IDE.lnk" "$INSTDIR\IDE\Cocos Code IDE.exe"

  WriteUninstaller $INSTDIR\uninstaller.exe
SectionEnd

Section "Uninstall"
  ; uninstall Cocos Studio
  ExecWait '"$INSTDIR\Cocos Studio\InstallData\uninstall.exe" "/U:$INSTDIR\Cocos Studio\InstallData\uninstall.xml" /S"'

  ; delete self (see explanation below why this works)
  Delete "$INSTDIR\uninstaller.exe"

  ; delete desktop icon
  ; Delete "$desktop\AnySDK.lnk"
  Delete "$desktop\Cocos Code IDE.lnk"
  ; Delete "$desktop\${PRODUCTNAME}.lnk"

  ; remove registry
  SetRegView ${RegView}
  DeleteRegValue HKLM "Software\Cocos" "InstallDir"

  RMDir /r /REBOOTOK "$INSTDIR"
SectionEnd

LangString DESC_Tools ${LANG_ENGLISH} "The tools include Cocos Studio, Cocos Code IDE."
LangString DESC_Framework ${LANG_ENGLISH} "The cocos2d-x frameworks."
LangString DESC_Prebuilt ${LANG_ENGLISH} "The prebuilt libs for cocos2d-x."
LangString DESC_Source ${LANG_ENGLISH} "The source code of cocos2d-x."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SectionFramework} $(DESC_Framework)
  !insertmacro MUI_DESCRIPTION_TEXT ${SectionTools} $(DESC_Tools)
  !insertmacro MUI_DESCRIPTION_TEXT ${SectionPrebuilt} $(DESC_Prebuilt)
  !insertmacro MUI_DESCRIPTION_TEXT ${SectionSource} $(DESC_Source)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Function dir_leave

  Var /GLOBAL spacePos
  ${StrLoc} $spacePos "$INSTDIR" " " >
  ${If} $spacePos != ""
    MessageBox MB_ICONSTOP|MB_OK '"$INSTDIR" should not contain space.'
    Abort
  ${EndIf}
Functionend

# Function LaunchLink
#   ExecShell "" "${StudioDir}\CocosStudio.Launcher.exe"
# FunctionEnd

Function fnc_SamplesDir_Leave
  ${NSD_GetText} $hCtl_SamplesDir_DirRequest1_Txt $0
  StrCpy $samplesDir $0

  Var /GLOBAL endChar
  StrCpy $endChar $samplesDir "" -1
  ${While} $endChar == "\"
    StrCpy $samplesDir $samplesDir -1
    StrCpy $endChar $samplesDir "" -1
  ${EndWhile}

FunctionEnd

Function GetWindowsVersion
 
  Push $R0
  Push $R1
 
  ClearErrors
 
  ReadRegStr $R0 HKLM \
  "SOFTWARE\Microsoft\Windows NT\CurrentVersion" CurrentVersion
 
  IfErrors 0 lbl_winnt
 
  ; we are not NT
  ReadRegStr $R0 HKLM \
  "SOFTWARE\Microsoft\Windows\CurrentVersion" VersionNumber
 
  StrCpy $R1 $R0 1
  StrCmp $R1 '4' 0 lbl_error
 
  StrCpy $R1 $R0 3
 
  StrCmp $R1 '4.0' lbl_win32_95
  StrCmp $R1 '4.9' lbl_win32_ME lbl_win32_98
 
  lbl_win32_95:
    StrCpy $R0 '95'
  Goto lbl_done
 
  lbl_win32_98:
    StrCpy $R0 '98'
  Goto lbl_done
 
  lbl_win32_ME:
    StrCpy $R0 'ME'
  Goto lbl_done
 
  lbl_winnt:
 
  StrCpy $R1 $R0 1
 
  StrCmp $R1 '3' lbl_winnt_x
  StrCmp $R1 '4' lbl_winnt_x
 
  StrCpy $R1 $R0 3
 
  StrCmp $R1 '5.0' lbl_winnt_2000
  StrCmp $R1 '5.1' lbl_winnt_XP
  StrCmp $R1 '5.2' lbl_winnt_2003
  StrCmp $R1 '6.0' lbl_winnt_vista
  StrCmp $R1 '6.1' lbl_winnt_7
  StrCmp $R1 '6.2' lbl_winnt_8
  StrCmp $R1 '6.3' lbl_winnt_81
  StrCmp $R1 '6.4' lbl_winnt_10 lbl_error
 
  lbl_winnt_x:
    StrCpy $R0 "NT $R0" 6
  Goto lbl_done
 
  lbl_winnt_2000:
    Strcpy $R0 '2000'
  Goto lbl_done
 
  lbl_winnt_XP:
    Strcpy $R0 'XP'
  Goto lbl_done
 
  lbl_winnt_2003:
    Strcpy $R0 '2003'
  Goto lbl_done
 
  lbl_winnt_vista:
    Strcpy $R0 'Vista'
  Goto lbl_done
 
  lbl_winnt_7:
    Strcpy $R0 '7'
  Goto lbl_done
 
  lbl_winnt_8:
    Strcpy $R0 '8'
  Goto lbl_done
 
  lbl_winnt_81:
    Strcpy $R0 '8.1'
  Goto lbl_done
 
  lbl_winnt_10:
    Strcpy $R0 '10.0'
  Goto lbl_done
 
  lbl_error:
    Strcpy $R0 ''
  lbl_done:
 
  Pop $R1
  Exch $R0
 
FunctionEnd
 
!macro GetWindowsVersion OUTPUT_VALUE
  Call GetWindowsVersion
  Pop `${OUTPUT_VALUE}`
!macroend
 
!define GetWindowsVersion '!insertmacro "GetWindowsVersion"'

Function .onInit
  Var /GLOBAL winBit
  Var /GLOBAL winVersion
  Var /GLOBAL spValue
  Var /GLOBAL typeValue
  Var /GLOBAL checkStr

  ${GetWindowsVersion} $winVersion

  ${If} ${RunningX64}
    StrCpy $winBit "64"
  ${Else}
    StrCpy $winBit "32"
  ${EndIf}

  ${If} ${IsServicePack} 0
    StrCpy $spValue "0"
  ${Else}
    StrCpy $spValue ""
  ${EndIf}

  System::Call kernel32::GetProductInfo(i6,i0,i0,i0,*i.r0)
  StrCpy $typeValue $0

  StrCpy $checkStr "Win$winVersion-$winBit-$spValue-Type$typeValue"
  ${If} $checkStr == "Win8.1-32-0-Type48"
    SetRebootFlag true
  ${OrIf} $checkStr == "Win8.1-32-0-Type101"
    SetRebootFlag true
  ${OrIf} $checkStr == "Win8.1-64-0-Type101"
    SetRebootFlag true
  ${EndIf}
FunctionEnd
