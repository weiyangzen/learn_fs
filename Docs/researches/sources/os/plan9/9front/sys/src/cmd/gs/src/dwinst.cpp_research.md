# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwinst.cpp

## Role
C++ implementation of the Ghostscript Win32 installer backend (`CInstall`). It handles file copying/checking, Start Menu shortcut creation, registry updates, uninstall-log generation, and Add/Remove Programs uninstall registration.

## Contents
- Initializes COM in the constructor and uninitializes in the destructor.
- Stores source directory, file-list name, target directory, target Start Menu group, Programs folder, uninstall name, main directory, and temporary log filenames.
- Reads `filelist.txt`/`fontlist.txt`: first line uninstall name, second line main directory, remaining lines files to install.
- Recursively creates target directories for drive and UNC paths.
- Installs files by copying source files to target paths or, in no-copy mode, checking that sources exist.
- Creates temporary logs for newly installed files, old/new registry state, and old/new shell-link state.
- Uses COM `IShellLink`/`IPersistFile` to save Start Menu `.LNK` files and records pre-existing link details for restoration.
- Creates registry keys under `HKEY_LOCAL_MACHINE\SOFTWARE\<product>\<version>`, writes string values, and records old/new `.reg`-style state.
- Copies `uninstgs.exe` and writes `HKLM\...\Uninstall\<m_szUninstallName>` with `DisplayName` and `UninstallString`.
- Consolidates temporary logs into `uninstal.txt` with section separators.
- Looks up current-user or common Programs folder from registry.

## Important Interfaces
- Public `CInstall` methods in `dwinst.h`: initialization, target setters, file install, Start Menu begin/add/end, registry begin/key/value/end, uninstall writing, log creation, cleanup.
- Private helpers: `SetRegistryValue`, `CreateShellLink`, `CopyFileContents`, `ResetReadonly`.
- Free helper `reg_quote`.

## Dependencies And Coupling
- Includes Win32, COM, shell APIs, stdio, direct I/O, and `dwinst.h`.
- Used by `dwsetup.cpp`.
- Uninstall log format is consumed by `dwuninst.cpp`; section names and field names must remain compatible.
- Uses `HKEY_LOCAL_MACHINE`, so installation expects sufficient privileges for registry writes.

## Risks And Notes
- Heavy use of fixed-size `MAXSTR` buffers and `strcpy`/`strcat`/`sprintf`.
- `MakeDir` UNC detection checks `dirname[1] == '\\' && dirname[1] == '\\'`, likely meant to check both first and second characters.
- `MakeTemp` uses `mktemp`, which is race-prone.
- Some error paths close temporary files directly and may leave class members pointing at closed streams until cleanup.
- Start Menu logging field names must match uninstaller expectations; inconsistency would prevent restoration.

## Filesystem Relevance
Installer file operations only: directory creation, file copy/delete logging, temporary files, shortcut files. Not filesystem implementation.
