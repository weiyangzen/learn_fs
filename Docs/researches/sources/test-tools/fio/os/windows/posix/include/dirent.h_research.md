# sources/test-tools/fio/os/windows/posix/include/dirent.h

Purpose: declares a minimal POSIX `dirent` API for Windows builds.

Important APIs/types: `struct dirent` carries `d_ino` and `d_name[MAX_PATH]`; `struct dirent_ctx` stores a Win32 `HANDLE find_handle` and directory name; `DIR` aliases that context. It declares `opendir()`, `readdir()`, and `closedir()`.

Control flow and state: implemented by `posix.c` using `CreateFileA()`, `FindFirstFileA()`, `FindNextFile()`, and `FindClose()`. `readdir()` returns a static `struct dirent`, so results are overwritten by the next call.

Dependencies and integration: includes `<winsock2.h>` to get Windows types and `MAX_PATH`. It enables fio code that scans directories to compile on Windows.

Risks: not thread-safe because of static `readdir()` storage; paths longer than `MAX_PATH` are truncated or unsupported; `d_ino` is always zero. It is sufficient for listing names, not metadata-rich directory traversal.

Test signals: Windows directory scans with existing, missing, inaccessible, and long-path directories.
