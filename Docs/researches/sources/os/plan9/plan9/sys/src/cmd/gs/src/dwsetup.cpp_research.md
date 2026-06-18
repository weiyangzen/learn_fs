# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwsetup.cpp

Purpose: Win32 setup program for AFPL Ghostscript.

Major responsibilities:
- Interactive or batch installation of Ghostscript program files and optional fonts.
- Creates file lists from directory specs when invoked with `-title`, `-dir`, and `-list`.
- Provides installer dialog, folder browsing, log window, and Readme launcher.
- Uses `CInstall` to copy files, write registry entries, create Start Menu shortcuts, and build uninstall logs.
- Optionally creates `cidfmap` for CJK fonts by running installed `gswin32c.exe`.

Key flows:
- `WinMain` calls `init`, then either enters dialog message loop or completes batch install.
- `init` determines Windows version, source directory, command-line mode, default Program Files target, and initializes main dialog.
- `install_all` coordinates program install, optional font install, and Start Menu folder opening.
- `install_prog` copies files, writes `GS_DLL` and `GS_LIB`, creates Start Menu shortcuts, optionally backs up/writes `lib/cidfmap`, and writes uninstall metadata.
- `install_fonts` installs from `fontlist.txt` and writes font uninstall metadata unless no-copy mode.
- `make_filelist` recursively walks files and writes list files for packaging.

File/list behavior:
- `filelist.txt` and `fontlist.txt` first line: uninstall name.
- Second line: main directory for uninstall logs.
- Remaining lines: files to install.
- If target equals source, no-copy mode validates file existence without copying.

Risks/legacy notes:
- Uses many fixed-size buffers and unchecked `strcpy`/`strcat`.
- Uses custom command-line parser.
- `write_cidfmap` launches a hidden process and does not wait for success.
- `dirwalk` uses Win32 `FindFirstFile` recursion and does not deeply guard path length.
- Batch install defaults to all-users on NT.

Filesystem relevance: Significant as packaging/install file traversal, copy, and uninstall-log generation, but not filesystem implementation.
