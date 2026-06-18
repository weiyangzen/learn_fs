# sources/storage-engines/wiredtiger/tools/tsan_playground/api_gcc_atomics.h

Purpose: implements the playground API using GCC `__atomic` acquire/release load/store builtins.

Important APIs and control flow: `atomic_store_release()` calls `__atomic_store_n(var, value, __ATOMIC_RELEASE)`, `atomic_load_acquire()` calls `__atomic_load_n(var, __ATOMIC_ACQUIRE)`, and `get_mode()` returns `GCC atomics`.

State and persistence behavior: only updates in-memory shared counter state.

Dependencies and integration points: selected by `_GCC_ATOMICS`; requires compiler support for GNU atomic builtins.

Risks: this is the GNU builtin baseline and should be understood by TSAN, but behavior depends on compiler and sanitizer instrumentation.

Test signals: expected to run without TSAN data-race warnings if the acquire/release counter correctly orders message writes.
