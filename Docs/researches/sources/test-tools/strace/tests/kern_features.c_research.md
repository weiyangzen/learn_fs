<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kern_features.c -->
# sources/test-tools/strace/tests/kern_features.c

Purpose: Tests decoding of the SPARC-specific `kern_features` syscall and its feature-bit return value.

Important APIs/types/functions: Uses `raw_syscall_0(__NR_kern_features, &err)`, `test_kern_features`, `KERN_FEATURE_MIXED_MODE_STACK` expected strings, fault-injected return values, and `SKIP_MAIN_UNDEFINED`.

Control flow: For each requested injected return number, the helper performs the raw syscall, prints either an errno failure or a decoded bitmask selected from a table of expected return values.

State/persistence behavior: No persistent state; the syscall is a feature query and the test only formats return values.

Dependencies: Requires SPARC syscall availability and raw syscall helper support. The test is skipped elsewhere.

Integration points: Validates return-value decoding rather than argument decoding, which is a distinct strace path.

Risks: Feature bits can grow beyond the single named bit used here. Raw syscall calling conventions differ by architecture.

Test signals: Output maps injected return values to `KERN_FEATURE_MIXED_MODE_STACK` plus unknown-bit fallbacks or skips when unsupported.

Source read signal: complete file read for this research pass; file size 99 line(s), 2030 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kern_features.c -->
