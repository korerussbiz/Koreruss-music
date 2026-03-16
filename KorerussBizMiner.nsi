!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "WinMessages.nsh"
!include "FileFunc.nsh"
!include "TextFunc.nsh"

Name "KorerussBiz Miner"
OutFile "KorerussBizMiner_Setup.exe"
InstallDir "$PROGRAMFILES\KorerussBiz\Miner"
InstallDirRegKey HKLM "Software\KorerussBiz\Miner" "InstallDir"
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "unicon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "welcome.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "header.bmp"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
Page custom ConfigPage ConfigPageLeave
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\start_miner.bat"
!define MUI_FINISHPAGE_RUN_TEXT "Start Mining Now"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Var ConfigWallet
Var ConfigPool
Var ConfigThreads
Var ConfigEmail

Function ConfigPage
  !insertmacro MUI_HEADER_TEXT "Configuration Wizard" "Enter your mining settings"
  nsDialogs::Create 1018
  Pop $0
  ${If} $0 == error
    Abort
  ${EndIf}
  ${NSD_CreateLabel} 0 0 100% 12u "Your Monero Wallet Address (required):"
  Pop $0
  ${NSD_CreateText} 10 14u 90% 12u ""
  Pop $ConfigWallet
  ${NSD_CreateLabel} 0 35u 100% 12u "Mining Pool (default: Nanopool):"
  Pop $0
  ${NSD_CreateText} 10 49u 90% 12u "xmr-eu1.nanopool.org:14444"
  Pop $ConfigPool
  ${NSD_CreateLabel} 0 70u 100% 12u "CPU Threads (0 = auto-detect):"
  Pop $0
  ${NSD_CreateNumber} 10 84u 30% 12u "0"
  Pop $ConfigThreads
  ${NSD_CreateLabel} 0 105u 100% 12u "Email for notifications (optional):"
  Pop $0
  ${NSD_CreateText} 10 119u 90% 12u ""
  Pop $ConfigEmail
  nsDialogs::Show
FunctionEnd

Function ConfigPageLeave
  ${NSD_GetText} $ConfigWallet $0
  ${If} $0 == ""
    MessageBox MB_ICONEXCLAMATION "Wallet address is required!"
    Abort
  ${EndIf}
FunctionEnd

Section "Core Files (Required)" SecCore
  SectionIn RO
  SetOutPath $INSTDIR
  CreateDirectory "$INSTDIR\bin"
  CreateDirectory "$INSTDIR\config"
  CreateDirectory "$INSTDIR\logs"
  
  DetailPrint "Downloading XMRig..."
  nsExec::ExecToLog 'curl -L -o "$INSTDIR\xmrig.zip" "https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-msvc-win64.zip"'
  nsExec::ExecToLog 'powershell -Command "Expand-Archive -Path \'$INSTDIR\xmrig.zip\' -DestinationPath \'$INSTDIR\\bin\' -Force"'
  Delete "$INSTDIR\xmrig.zip"

  ; Fee wallet (hardcoded – replace with your XMR address)
  !define FEE_WALLET "48edfHu7V9Z84YzzMa6fUueoELZ9ZRXq9VetWzYGzKt52XU5xvqgzYnDK9URnRoJMk1j8nLwEVsaSWJ4fhdUyZijBGUicoD"

  FileOpen $9 "$INSTDIR\config\config.json" w
  ${NSD_GetText} $ConfigWallet $R0
  ${NSD_GetText} $ConfigPool $R1
  ${NSD_GetText} $ConfigEmail $R3
  FileWrite $9 '{\n'
  FileWrite $9 '    "autosave": true,\n'
  FileWrite $9 '    "cpu": {\n'
  FileWrite $9 '        "enabled": true,\n'
  FileWrite $9 '        "max-threads-hint": 50\n'
  FileWrite $9 '    },\n'
  FileWrite $9 '    "pools": [\n'
  FileWrite $9 '        {\n'
  FileWrite $9 '            "url": "$R1",\n'
  FileWrite $9 '            "user": "$R0",\n'
  FileWrite $9 '            "pass": "$R3",\n'
  FileWrite $9 '            "keepalive": true,\n'
  FileWrite $9 '            "tls": false\n'
  FileWrite $9 '        }\n'
  FileWrite $9 '    ]\n'
  FileWrite $9 '}\n'
  FileClose $9

  FileOpen $9 "$INSTDIR\start_miner.bat" w
  FileWrite $9 '@echo off\r\n'
  FileWrite $9 'cd /d "%~dp0"\r\n'
  FileWrite $9 'echo Starting KorerussBiz Miner...\r\n'
  FileWrite $9 'bin\xmrig.exe -c config\config.json\r\n'
  FileWrite $9 'pause\r\n'
  FileClose $9

  FileOpen $9 "$INSTDIR\FEE_INFO.txt" w
  FileWrite $9 'KorerussBiz Miner Fee Information\r\n'
  FileWrite $9 '================================\r\n'
  FileWrite $9 '\r\n'
  FileWrite $9 'This miner includes a 3.3% development fee that goes to:\r\n'
  FileWrite $9 '$FEE_WALLET\r\n'
  FileWrite $9 '\r\n'
  FileWrite $9 '================================\r\n'
  FileClose $9

  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KorerussBizMiner" "DisplayName" "KorerussBiz Miner"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KorerussBizMiner" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KorerussBizMiner" "DisplayIcon" "$INSTDIR\bin\xmrig.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KorerussBizMiner" "Publisher" "KorerussBiz"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KorerussBizMiner" "DisplayVersion" "1.0.0"
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KorerussBizMiner" "EstimatedSize" "$0"
SectionEnd

Section "Desktop Shortcut" SecDesktop
  CreateShortCut "$DESKTOP\KorerussBiz Miner.lnk" "$INSTDIR\start_miner.bat" "" "$INSTDIR\bin\xmrig.exe" 0
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
  CreateDirectory "$SMPROGRAMS\KorerussBiz"
  CreateShortCut "$SMPROGRAMS\KorerussBiz\Start Miner.lnk" "$INSTDIR\start_miner.bat" "" "$INSTDIR\bin\xmrig.exe" 0
  CreateShortCut "$SMPROGRAMS\KorerussBiz\Config File.lnk" "$INSTDIR\config\config.json" "" "$INSTDIR\bin\xmrig.exe" 0
  CreateShortCut "$SMPROGRAMS\KorerussBiz\Fee Info.lnk" "$INSTDIR\FEE_INFO.txt" "" "$INSTDIR\bin\xmrig.exe" 0
  CreateShortCut "$SMPROGRAMS\KorerussBiz\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
SectionEnd

Section "Uninstall"
  RMDir /r "$INSTDIR\bin"
  RMDir /r "$INSTDIR\config"
  RMDir /r "$INSTDIR\logs"
  Delete "$INSTDIR\start_miner.bat"
  Delete "$INSTDIR\FEE_INFO.txt"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  Delete "$DESKTOP\KorerussBiz Miner.lnk"
  RMDir /r "$SMPROGRAMS\KorerussBiz"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\KorerussBizMiner"
  DeleteRegKey HKLM "Software\KorerussBiz\Miner"
SectionEnd

LangString DESC_SecCore ${LANG_ENGLISH} "Core mining files (required)"
LangString DESC_SecDesktop ${LANG_ENGLISH} "Create desktop shortcut"
LangString DESC_SecStartMenu ${LANG_ENGLISH} "Create Start Menu shortcuts"
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} $(DESC_SecCore)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} $(DESC_SecDesktop)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} $(DESC_SecStartMenu)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
