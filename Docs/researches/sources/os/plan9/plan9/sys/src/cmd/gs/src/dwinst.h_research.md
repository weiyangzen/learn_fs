# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwinst.h

Purpose: Declares the `CInstall` class for the Windows Ghostscript installer.

Public capabilities:
- Configure message callback, target directory/group, and all-users mode.
- Initialize from source directory and file list.
- Install files, individual files, and make directories.
- Manage Start Menu entries.
- Begin/update/end registry modifications.
- Write uninstall metadata and consolidated uninstall logs.
- Clean up temporary files.
- Append extra generated files to the uninstall file list.

Private state:
- Source/list/target/group/programs paths.
- Uninstall name and main/log directories.
- Temporary log filenames for files, registry, and shell.
- Open log file handles.
- Internal helpers for shell links, registry values, file copying, and readonly-bit reset.

Filesystem relevance: Installer path/file bookkeeping declarations.
