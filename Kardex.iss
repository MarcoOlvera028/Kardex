[Setup]
AppName=Kardex
AppVersion=1.0
DefaultDirName={localappdata}\Kardex
DefaultGroupName=Kardex
OutputDir=installer
OutputBaseFilename=Setup_Kardex
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\Kardex\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Kardex"; Filename: "{app}\Kardex.exe"
Name: "{commondesktop}\Kardex"; Filename: "{app}\Kardex.exe"

[Run]
Filename: "{app}\Kardex.exe"; Description: "Ejecutar Kardex"; Flags: nowait postinstall skipifsilent
