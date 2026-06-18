# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwinst.h

## Role
Class declaration for the Ghostscript Win32 installer backend.

## Contents
- Defines `MAXSTR` from `MAX_PATH` or 256.
- Declares `CInstall` constructor/destructor and public methods for message callbacks, program/folder lookup, initialization, file installation, directory creation, temp file creation, all-users mode, target setters, Start Menu operations, registry operations, uninstall entry/log generation, cleanup, and appending installed-file records.
- Stores installer state, paths, log filenames, log stream pointers, and message callback.
- Declares private helpers for registry value writing, shell-link creation, file copying, and readonly attribute reset.

## Important Interfaces
- `CInstall` public API is the contract used by `dwsetup.cpp`.

## Dependencies And Coupling
- Requires Win32 types (`BOOL`, `HKEY`, `LPCSTR`) and `FILE`.
- Paired with `dwinst.cpp`.

## Risks And Notes
- Path buffers are fixed-size and public methods accept raw C strings.
- Members `m_bNoCopy`, `m_bQuit`, and some flags are declared but not central in the implementation, suggesting historical leftovers.

## Filesystem Relevance
Installer helper abstraction for filesystem copy/log operations.
