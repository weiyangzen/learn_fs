# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwinst.cpp

Purpose: C++ helper class implementing Windows Ghostscript installation operations.

Class: `CInstall`.

Main responsibilities:
- Initializes install source/list metadata.
- Copies listed files or validates them in no-copy mode.
- Creates directories recursively.
- Creates Start Menu folders and shell links via COM `IShellLink`/`IPersistFile`.
- Writes and records registry updates.
- Copies uninstaller and writes Add/Remove Programs uninstall keys.
- Builds consolidated uninstall logs from temporary file/registry/shell logs.
- Provides Start Menu folder lookup.

Key methods:
- Lifecycle/message: constructor/destructor, `CleanUp`, `SetMessageFunction`, `AddMessage`.
- Paths/init: `SetTargetDir`, `SetTargetGroup`, `Init`, `GetMainDir`, `GetUninstallName`, `GetPrograms`, `SetAllUsers`.
- File copy: `InstallFiles`, `InstallFile`, `AppendFileNew`, `MakeDir`, `ResetReadonly`.
- Shell: `StartMenuBegin`, `StartMenuAdd`, `StartMenuEnd`, `CreateShellLink`.
- Registry: `UpdateRegistryBegin`, `UpdateRegistryKey`, `UpdateRegistryValue`, `SetRegistryValue`, `UpdateRegistryEnd`.
- Uninstall/logging: `WriteUninstall`, `MakeTemp`, `MakeLog`, `CopyFileContents`.

Important details:
- Installer file lists use the first line as uninstall name, second line as main directory, subsequent lines as files.
- Registry update logs are written in `REGEDIT4`-style form for later uninstall restore/delete.
- `MakeTemp` uses `mktemp`, making it race-prone by modern standards.
- `MakeDir` has a UNC-path typo: `dirname[1]=='\\' && dirname[1]=='\\'` should likely test indexes 0 and 1.
- String handling is mostly fixed-buffer `strcpy`/`strcat`/`sprintf`.

Filesystem relevance: File installation/uninstallation and directory creation behavior, but only for Windows Ghostscript packaging.
