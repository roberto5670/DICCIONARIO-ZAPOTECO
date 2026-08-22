[Setup]
AppId={{C8E91F24-89AB-4F12-8800-D1F3419041A3}}
AppName=Diccionario Zapoteco
AppVersion=1.0
AppPublisher=Roberto Hernández
DefaultDirName={autopf}\Diccionario Zapoteco
DefaultGroupName=Diccionario Zapoteco
UninstallDisplayIcon={app}\app.exe
Compression=lzma2/ultra64
SolidCompression=yes
OutputDir=Output
OutputBaseFilename=Setup_Diccionario_Zapoteco
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Diccionario Zapoteco"; Filename: "{app}\app.exe"
Name: "{autodesktop}\Diccionario Zapoteco"; Filename: "{app}\app.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\app.exe"; Description: "{cm:LaunchProgram,Diccionario Zapoteco}"; Flags: nowait postinstall skipifsilent