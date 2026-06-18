# sources/test-tools/xfstests-bld/fstests-bld/android-compat/getpwent.c

Purpose: simulates passwd database iteration for Android builds, exposing `root` and `fsgqa` users required by filesystem tests.

Important APIs and functions: static `entries[]`, `current_pw`, exported `getpwent()` and `setpwent()`, disabled `endpwent()`, and debug-only `getpwnam`, `getpwuid`, `print_passwd`, and `main`.

Control flow: `getpwent` lazily starts at the first entry and advances until a null sentinel. `setpwent` resets iteration.

State and persistence: static iteration pointer is process-global. It does not consult `/etc/passwd`.

Dependencies and integration: compiled into Android compatibility library for xfstests tools that enumerate users.

Risks: `setpwent` is declared `int` but does not return a value, which can produce warnings or undefined return values. The implementation is not thread-safe and covers only two users.

Test signals: debug main validates lookup behavior for root, fsgqa, and absent entries.
