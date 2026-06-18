# sources/sync-backup/git-crypt/coprocess.cpp

Purpose: platform-selection translation unit for the `Coprocess` implementation.

Important APIs/types/functions: conditionally includes `coprocess-win32.cpp` when `_WIN32` is defined, otherwise includes `coprocess-unix.cpp`.

Control flow: compile-time include selection only. The Makefile compiles `coprocess.cpp`, so the chosen platform implementation becomes part of `coprocess.o`.

State/persistence behavior: no state in this file; state lives in the selected implementation.

Dependencies/integration: pairs with `coprocess.hpp`, which similarly selects the platform header. This inclusion pattern explains the Makefile dependency on both platform source files.

Risks/test signals: unusual `.cpp` inclusion can surprise build tooling and dependency scanners. Test signals are successful single-definition builds on Windows and Unix and correct rebuilds when platform-specific files change.
