# sources/test-tools/strace/src/static_assert.h

Purpose: portability wrapper for `static_assert` across compilers and C language levels.

Important APIs/types/functions: includes `assert.h`, maps to existing `static_assert` or `_Static_assert`, and provides a GNU-compatible extern-array fallback.

Control flow: preprocessor chooses the native/static assertion mechanism when available. If neither is available, the fallback creates an extern function declaration whose array size is invalid when the expression is false.

State and persistence behavior: compile-time only; no runtime state.

Dependencies and integration points: widely included by files that validate local ABI structs against kernel sizes.

Risks: fallback uses a declaration form and suppresses nested-extern warnings under GCC; portability to non-GNU compilers without static assertions is limited.

Test signals: build with C11 static assertions, compiler `_Static_assert`, and fallback configurations; verify both passing and intentionally failing assertions behave at compile time.
