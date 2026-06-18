## sources/test-tools/stress-ng/stress-umask.c

Purpose: Implements `umask`, exercising process umask semantics together with create/stat/close/unlink filesystem operations.

Important APIs/types/functions: `stress_umask_info` and `stress_umask`; uses `umask`, `open(O_CREAT)`, `fstat`, `unlink`, stress-ng temporary directory/name helpers, and random mask generation.

Control flow: saves original umask, creates a temp directory, synchronizes, then iterates all masks from `0000` to `0777`. For each mask it verifies `umask` returned the previous mask, creates a mode `0777` file, verifies effective file permissions equal `~mask & 0777`, closes and unlinks it. It then performs random mask round-trip checks.

State and persistence: mutates process umask but restores the original mask on all exit paths; creates and removes temporary files/directories per iteration.

Dependencies/integration: uses stress-ng temp filesystem helpers, bogo counters, and `VERIFY_ALWAYS`.

Risks: umask is process-global, so unexpected control-flow changes must restore it; filesystem ACL/default-mode behavior could influence permission expectations on unusual filesystems.

Test signals: failures report invalid returned masks, mode mismatches, create/stat/unlink errors; one bogo increment covers a full sweep plus random checks.
