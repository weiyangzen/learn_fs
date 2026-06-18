# sources/storage-engines/sqlite/src/os_setup.h

Purpose: normalizes compile-time operating-system selection for SQLite. After preprocessing, exactly one of `SQLITE_OS_KV`, `SQLITE_OS_OTHER`, `SQLITE_OS_UNIX`, or `SQLITE_OS_WIN` should be active, with the others forced to zero.

Important macros: if no OS macro is predefined, Windows-like compiler/platform macros select `SQLITE_OS_WIN=1`; otherwise Unix is selected. Explicit `SQLITE_OS_OTHER`, `SQLITE_OS_KV`, `SQLITE_OS_UNIX`, or `SQLITE_OS_WIN` overrides clear the other OS flags. `SQLITE_OS_KV` additionally defines storage-engine-limiting options: omit loadable extensions, WAL, deprecated APIs, shared cache, and autoinit; force memory temp store; and set `SQLITE_DQS=0`.

Control flow: all behavior is preprocessor logic. The `+1<=1` and `+1>1` tests distinguish undefined/zero from positive macro values without requiring prior definitions.

State and persistence: no runtime state. The selected macros determine which VFS, mutex backend, and feature set are compiled.

Dependencies and integration points: included by `os.h` before mutex selection in `mutex.h` relies on `SQLITE_OS_UNIX` or `SQLITE_OS_WIN`. It governs compilation of platform files such as `os_unix.c`, `os_win.c`, and `os_kv.c`.

Risks: incorrect or conflicting OS macro definitions can compile the wrong VFS or disable required features. `SQLITE_OS_KV` is intentionally restrictive; enabling it in a normal native build would omit WAL, shared cache, autoinit, and extension loading. Build systems must define only one positive OS target.

Test signals: preprocess builds for Windows, Unix, OS_OTHER, and OS_KV and inspect macro results; compile minimal custom-VFS builds with `SQLITE_OS_OTHER=1`; run kvvfs builds to verify the forced feature omissions; and check mutex backend selection after OS detection.
