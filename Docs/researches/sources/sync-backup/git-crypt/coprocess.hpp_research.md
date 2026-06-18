# sources/sync-backup/git-crypt/coprocess.hpp

Purpose: platform-selection header for the `Coprocess` class.

Important APIs/types/functions: includes `coprocess-win32.hpp` on `_WIN32`, otherwise `coprocess-unix.hpp`.

Control flow: compile-time selection only. Consumers include `coprocess.hpp` and get the right platform class declaration.

State/persistence behavior: no direct state; selected headers define process and pipe handle state.

Dependencies/integration: centralizes platform choice for `util.cpp` and command helpers, avoiding conditional code at call sites.

Risks/test signals: platform macros must be consistent between this header and `coprocess.cpp`. Build tests on both Windows and Unix are the primary signal.
