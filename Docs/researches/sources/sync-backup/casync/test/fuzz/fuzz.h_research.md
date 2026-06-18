# sources/sync-backup/casync/test/fuzz/fuzz.h

Purpose: shared declaration for casync fuzz harnesses.

Important APIs/types/functions: declares the libFuzzer-compatible `LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)` entry point.

Control flow/state: no state. Provides a common interface so `fuzz-main.c` can call individual fuzz target objects.

Dependencies/integration: included by fuzz target files and the standalone runner.

Risks/test signals: API must remain ABI-compatible with libFuzzer. Any target-specific initialization must live outside this minimal header.

Source research group: `subset-b-009122`.
