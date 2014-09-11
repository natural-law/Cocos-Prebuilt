; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Cocos Creator"
#define MyAppVersion "3.1"
#define MyAppPublisher "Chukong-inc"
#define MyAppURL "http://www.cocos2d-x.org/"
#define MyExeName "Cocos Code IDE"
#define MyAppExeName "IDE\Cocos Code IDE.exe"
#define MyRootDir "..\..\.."
#define MyInstallGroupName "cocos"

#define StudioInstaller "CocosStudio.exe"
#define StudioSetupINI "studiosetup.ini"
#define RunFirstBat "cocos_runfirst.bat"

#define IDEPath "IDE\Cocos Code IDE.exe"
#define IDEExeName "Cocos Code IDE.exe"
#define AnySDKPath "AnySDK\bin\AnySDK.exe"
#define AnySDKExeName "AnySDK.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{25521E37-D0A4-4510-8400-5E1933112AA1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultGroupName={#MyInstallGroupName}
DefaultDirName={pf}\{#MyInstallGroupName}
AllowNoIcons=yes
LicenseFile=..\resources-common\license.txt
;InfoBeforeFile=..\resources-common\BeforeInstall.txt
;InfoAfterFile=..\resources-common\AfterInstall.txt
OutputDir={#MyRootDir}\release
OutputBaseFilename={#MyAppName}-{#BitFlag}
Compression=lzma
SolidCompression=yes
SetupIconFile=resources\Icon.ico
WizardImageFile=resources\wizard.bmp
WizardSmallImageFile=resources\smallicon.bmp

[Files]
Source: "{#MyRootDir}\gen\cocos\frameworks\*"; DestDir: "{app}\frameworks"; Excludes: ".DS_Store"; Flags: recursesubdirs
Source: "{#MyRootDir}\gen-win32\{#BitFlag}\*"; DestDir: "{app}"; Excludes: ".DS_Store"; Flags: recursesubdirs
Source: "{#MyRootDir}\gen-win32\{#StudioInstaller}"; DestDir: "{tmp}"
Source: "resources\{#RunFirstBat}"; DestDir: "{tmp}"

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

;[Messages]
;WelcomeLabel1=Welcome to the [name] Setup Wizard
;WelcomeLabel2=This will install [name/ver] on your computer.%n%n

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Icons]
Name: "{group}\{#IDEExeName}"; Filename: "{app}\{#IDEPath}"
Name: "{group}\{#AnySDKExeName}"; Filename: "{app}\{#AnySDKPath}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Cocos Code IDE.exe"; Filename: "{app}\{#IDEPath}"; Tasks: desktopicon
Name: "{commondesktop}\AnySDK.exe"; Filename: "{app}\{#AnySDKPath}"; Tasks: desktopicon

[Run]
Filename: "{tmp}\{#RunFirstBat}"; Parameters: """{tmp}\{#StudioSetupINI}"" ""{app}\Cocos Studio"""; StatusMsg: "Writing configuration..."
Filename: "{tmp}\{#StudioInstaller}"; Parameters: """/S:{tmp}\{#StudioSetupINI}"" /NOINIT"; StatusMsg: "Installing Cocos Studio..."
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyExeName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{app}\Cocos Studio\InstallData\uninstall.exe"; Parameters: """/U:{app}\Cocos Studio\InstallData\uninstall.xml"" /S"; Flags: skipifdoesntexist