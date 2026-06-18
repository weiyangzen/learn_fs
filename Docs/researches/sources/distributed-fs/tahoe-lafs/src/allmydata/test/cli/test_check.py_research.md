# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_check.py

## Purpose
Tests `tahoe check`, `deep-check`, `manifest`, and related stats behavior across healthy, unhealthy, corrupt, repairable, literal, immutable, mutable, and unrecoverable objects.

## Important APIs, Types, And Functions
`Check` combines no-network grid helpers and CLI helpers. `test_check()` creates a mutable file, literal file, and literal directory, runs normal/raw/verify/repair checks, corrupts and deletes shares, and validates human and JSON output. `test_deep_check()` builds a directory tree with Unicode, literal, immutable, and mutable children, checks verbose and raw traversal output, validates stats, corrupts shares, repairs, then creates an unrecoverable subdirectory. Remaining tests cover missing alias, nonexistent alias, and multiple URI arguments.

## Control Flow
The tests chain Deferred callbacks: create objects, stash URIs, run CLI commands, parse output, mutate local share files with `os.unlink()` and `debug.corrupt_share()`, and rerun checks with `--verify` and `--repair`. Deep-check traversal emits per-object lines and final summaries; unrecoverable traversal should stop with an error rather than a misleading `done:` line.

## State And Persistence
State lives in the temporary no-network grid and local share files. Tests directly delete or corrupt shares to create known health states and store URIs in instance dictionaries for later traversal and repair checks.

## Dependencies And Integration Points
Depends on Tahoe URI parsing, mutable publish data, immutable upload data, debug corruption command, base32 formatting, encoding output quoting, no-network grid helpers, CLI common mixin, JSON output, and filesystem share discovery helpers.

## Risks And Test Signals
Risks include health-summary drift, raw JSON schema changes, verifier-only corruption detection, repair reporting mismatches, Unicode path quoting regressions, stats miscounts, and alias error handling. Signals include expected summaries for healthy/LIT/unhealthy objects, good-share and corrupt-share counts, corrupt share location lines, repair success then restored health, deep-check pre/post repair summaries, raw line counts, stats histogram lines, and nonzero errors for unrecoverable directories without a final `done:`.
