# sources/test-tools/fio/os/windows/posix/include/dlfcn.h

Purpose: provides a small `<dlfcn.h>` facade for dynamic loading on Windows.

Important APIs/types: defines `RTLD_LAZY` and declares `dlopen()`, `dlclose()`, `dlsym()`, and `dlerror()`.

Control flow and state: `posix.c` maps these to `LoadLibrary()`, `FreeLibrary()`, `GetProcAddress()`, and a global string pointer for the last error.

Dependencies and integration: supports fio code that loads engines or optional modules through Unix-style dynamic-loader calls.

Risks: `mode` is ignored; `dlerror()` returns coarse static strings, not detailed Win32 errors; the global error pointer is not thread-local. `LoadLibrary()` path semantics differ from POSIX `dlopen()`.

Test signals: load a known DLL, resolve an exported symbol, fail a missing symbol, and ensure caller paths handle the simplified error reporting.
