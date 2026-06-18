# sources/sync-backup/unison/src/system/system_win_stubs.c

Purpose: Windows system stubs for accurate stat/lstat metadata, console detection/initialization, console modes/code pages, and VT capability.

Important APIs: `win_has_correct_ctime`, `win_stat(path,lstat)`, `win_hasconsole_gui_stdout`, `win_hasconsole_gui_stderr`, `win_init_console`, `win_get_console_mode`, `win_set_console_mode`, `win_get_console_output_cp`, `win_set_console_output_cp`, and `win_vt_capable`.

Control flow: `win_init` dynamically resolves `NtQueryInformationFile` and `RtlNtStatusToDosError` from `ntdll`. `win_stat` opens the path with backup semantics and optionally reparse-point behavior, uses NT file information when available, falls back to `GetFileInformationByHandle`, detects symlink reparse points for `lstat`, computes device/inode/kind/mode/nlink/size/times, and returns an OCaml stat tuple. Console code detects GUI-only output, allocates or repairs consoles, restores C runtime stdio, and returns optional handles for streams that were not redirected.

State/persistence: reads file metadata and may allocate a console or change console mode/code page. Maintains cached NT API availability and `CONIN$` handle.

Dependencies/integration: Windows kernel/NT APIs, libuv-derived struct definitions, OCaml runtime compatibility shims, GUI/text UI startup, and file scanning code.

Risks: NT struct compatibility and dynamic resolution are delicate. Inode hashing and fallback behavior affect archive identity. The console repair path addresses rare invalid inherited handle cases and must avoid breaking legitimate redirection. Recursive call from `lstat` to `stat` for non-symlinks must preserve error semantics.

Test signals: Windows stat/lstat tests for files, dirs, symlinks, reparse points, link counts, ctime behavior, GUI console startup under cmd/PowerShell/Cygwin/MSYS2, redirected stdout/stderr, code-page changes, and VT detection.
