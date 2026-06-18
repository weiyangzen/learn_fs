## sources/test-tools/stress-ng/stress-vecmath.c

Purpose: Implements `vecmath`, a deterministic integer vector arithmetic stressor.

Important APIs/types/functions: `stress_vecmath_info` and `stress_vecmath`; uses vector typedefs, constant-building macros, `OPS` arithmetic/bitwise/shift/mod/div swap operations, `TARGET_CLONES`, SIGILL catch, and stress put sinks.

Control flow: initializes vectors for multiple lane widths, repeats a large mixed operation schedule, increments bogo, then folds each vector width into scalar checksums. Any checksum mismatch marks failure and exits the loop.

State and persistence: stack/register-local only; no persistent resources.

Dependencies/integration: `HAVE_VECMATH`, optional `HAVE_INT128_T`, architecture-specific target clone handling, CPU/vector classifier.

Risks: vector modulo/division and shifts across signed vector lane types are compiler-extension heavy; architecture/compiler differences may reveal bugs. Runtime SIGILL handling is needed for cloned paths on CPUs lacking selected instructions.

Test signals: `VERIFY_ALWAYS`; fixed expected checksums validate 8/16/32/64/optional 128-bit results.
