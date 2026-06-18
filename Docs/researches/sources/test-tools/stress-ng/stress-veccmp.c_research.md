## sources/test-tools/stress-ng/stress-veccmp.c

Purpose: Implements `veccmp`, a compiler-vector integer comparison stressor with deterministic checksum validation.

Important APIs/types/functions: `stress_veccmp_info` and `stress_veccmp`; uses vector typedefs for 8/16/32/64-bit lanes and optional 128-bit lanes, constants assembled by macros, `OPS` comparison macro, `TARGET_CLONES`, SIGILL catch, and `stress_put_*` sinks.

Control flow: after sync, each loop initializes vector registers from constants, performs repeated greater/less/equal/not-equal comparison mixes across vector widths, folds the resulting vectors into scalar checksums, compares them against fixed expected values, and increments bogo on success.

State and persistence: all computation state is stack/register-local; no heap or file state.

Dependencies/integration: compile gated on `HAVE_VECMATH` and compiler version support; integrates with CPU/vector classifiers and mandatory verification.

Risks: compiler vector semantics and target-clone codegen can vary by architecture; SIGILL handling protects unsupported runtime CPU paths, but checksum mismatches indicate real compiler/CPU bugs or changed semantics.

Test signals: `VERIFY_ALWAYS`; per-width checksum failures are explicit.
