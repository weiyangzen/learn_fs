# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwsetup.cpp

## Role
Win32 setup application for AFPL Ghostscript. It provides interactive and batch installation, drives `CInstall`, creates file lists, writes registry/search-path values, creates Start Menu shortcuts, optionally installs fonts/CJK support, and launches uninstall setup.

## Contents
- Documents expected self-extracting archive contents and `filelist.txt`/`fontlist.txt` format.
- Defines global installer state: source directory, target directory, Start Menu group, app name, flags for batch/no-copy/fonts/CJK/all-users, dialog handles, and quit/error flags.
- `WinMain` calls `init`, then runs the message loop for interactive mode.
- Provides a modeless install log dialog with copy-to-clipboard support and rolling text buffer.
- Provides a simple directory/group browse dialog using `DlgDirList`/`DlgDirSelectEx`.
- `init` validates Windows version, parses command line, supports file-list creation mode, batch install mode, and interactive dialog setup.
- `install_all` runs program and optional font installation, handles no-copy mode, displays log, and opens the Start Menu folder on success.
- `install_prog` copies program files, calculates version from main directory name, writes `GS_DLL` and `GS_LIB` under `HKLM\SOFTWARE\AFPL Ghostscript\<version>`, creates Start Menu links to `gswin32.exe` and `Readme.htm`, optionally rewrites `lib\cidfmap`, writes uninstall logs, and registers uninstall.
- `install_fonts` copies font files and writes font uninstall logs unless in no-copy mode.
- `get_font_path` and `write_cidfmap` build Windows fonts path and launch hidden `gswin32c.exe` with `mkcidfm.ps` to generate `cidfmap`.
- `dirwalk` and `make_filelist` create file-list manifests from path specs or `@file` lists.
- `GetProgramFiles` dynamically resolves shell folder APIs or falls back to registry.

## Important Interfaces
- Entry point `WinMain`.
- Dialog procs `TextWinDlgProc`, `DirDlgProc`, `MainDlgProc`.
- Installation routines `install_all`, `install_prog`, `install_fonts`.
- Manifest helpers `dirwalk`, `make_filelist`.
- Utility `GetProgramFiles`.

## Dependencies And Coupling
- Uses `CInstall` from `dwinst.cpp`.
- Uses resource IDs from `dwsetup.h`.
- Produces uninstall logs consumed by `dwuninst.cpp`.
- Requires `filelist.txt`, optionally `fontlist.txt`, and a source tree with Ghostscript binaries/libs.
- Uses Shell/COM/registry APIs and may require privileges for HKLM and common Start Menu writes.

## Risks And Notes
- Manual command-line parser has limited quote handling.
- Extensive fixed-size buffer concatenation.
- `write_cidfmap` starts Ghostscript and returns success without waiting for or checking the child process result.
- Batch mode suppresses UI unless errors occur.
- File-list generation recursively walks directories through Win32 `FindFirstFile`.

## Filesystem Relevance
Installer/file-list generation code: copies files, creates directories, launches files, writes generated config files. Not filesystem implementation.
