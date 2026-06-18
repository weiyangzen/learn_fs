# sources/test-tools/cthon04/general/large3.c

Purpose: generated copy of general/large.c completing the four-way large compile workload.

Important APIs/types/functions: identical to large.c in this checkout, including main(), compiler-pass path globals, suffix helpers, fork/exec wrapper, and string-save allocator.

Control flow: same cc-like pass orchestration as large.c.

State and persistence behavior: generated source artifact; compilation creates a temporary binary that large4.sh removes.

Dependencies and integration points: produced by the general Makefile and compiled alongside large.c, large1.c, and large2.c.

Risks: regeneration overwrites local edits; old K&R assumptions and hard-coded paths apply.

Test signals: generated copy exists and compiles successfully in the general test script.
