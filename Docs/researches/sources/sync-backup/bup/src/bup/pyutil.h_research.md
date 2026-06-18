## sources/sync-backup/bup/src/bup/pyutil.h

Purpose: shared C/Python utility header for allocation, Python integer conversion, and integral assignment checks.

Important APIs: declares checked allocation and unsigned conversion helpers. `BUP_LONGISH_TO_PY(x)` chooses signed or unsigned Python long creation based on expression signedness. `BUP_ASSIGN_PYLONG_TO_INTEGRAL(dest, pylong, overflow)` assigns a Python integer into an arbitrary integral destination, distinguishing Python overflow from C range overflow.

State and dependencies: macro-only plus declarations; depends on `sys/types.h` and `intprops.h`, and assumes Python headers are already available in translation units using Python APIs.

Risks and tests: the assignment macro uses GNU statement-expression syntax, so portability depends on supported compilers. Callers must inspect both return value and overflow flag. Indirect test coverage comes from C extension behavior.
