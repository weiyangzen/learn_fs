# sources/test-tools/stress-ng/stress-landlock.c

Purpose: implements `landlock`, a Linux Landlock LSM stressor that creates rulesets, adds path-beneath rules with many access masks, restricts child processes, and recursively consumes Landlock resources.

Important APIs/types/functions: shim access macros provide fallback bit definitions for newer Landlock flags. `stress_landlock_ctxt_t` carries mask, active flag, filename, and base path. Syscall wrappers cover `landlock_create_ruleset`, `landlock_add_rule`, and `landlock_restrict_self`. `stress_landlock_get_access_mask()` discovers usable access bits.

Control flow: support probing creates a minimal ruleset. The main stressor builds a temp filename, discovers usable mask, forks a background child that recursively scans `/` and adds read-file rules where possible, sync-starts, then loops over cumulative and single access flag combinations. Each test forks an isolated child, creates a file, creates a ruleset, opens the temp path with `O_PATH`, adds a path-beneath rule, sets `PR_SET_NO_NEW_PRIVS`, restricts itself, and probes read/write opens before exiting.

State and persistence behavior: restriction state is confined to forked children because Landlock is irreversible for a task. Temporary files are unlinked after each child. Background traversal allocates and closes rulesets without applying them to the parent.

Dependencies and integration points: requires Linux Landlock headers, rule types, and syscalls plus `prctl`. Uses stress-ng fork retry, temp path, dirent, kill, and process state helpers. Registered as `CLASS_OS`.

Risks: Landlock support depends on kernel version and `lsm=landlock`. Recursive scanning of `/` can be expensive and permission noisy. Newer access bits are masked to `0xffff`, so future Landlock bits may not be covered.

Test signals: confirm skip when Landlock is unavailable, successful runs on enabled kernels, no leftover temp files, bounded failure count, and cleanup of the background ruleset-consuming child.
