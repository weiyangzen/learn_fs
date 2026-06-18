# sources/sync-backup/unison/dev/check-memory

Purpose: POSIX shell developer experiment to estimate memory/stack limits needed for Unison syncs with many files.

Important functions: `log`, `fatal`, `goto_dir`, `fini`, `init_N_M`, `touch_N_M_all`, `limit`, `limit_display`, `start_server`, `do_sync`, `simple_test`, and `all`.

Control flow: creates `/tmp/UNISON-TEST`, initializes `local` with `N*M` files, applies `ulimit` constraints for data/RSS/stack, starts a socket-mode Unison server with isolated `UNISON` archive directories, runs a batch sync, touches every local file, runs a second sync, logs parseable `sync` result lines, then removes generated state.

State/persistence: owns `/tmp/UNISON-TEST`, `local`, `remote`, `.unison.local`, `.unison.remote`, and socket `s`. It refuses to start if `local` or `remote` already exists to avoid accidental data loss.

Dependencies/integration: requires `unison` in PATH, POSIX shell tools, `seq`, `find`, `date`, `ulimit`, and socket support.

Risks: comments note it is a work in progress. `ulimit` flags vary substantially by OS and may not constrain malloc consistently. Cleanup uses `rm -rf` but checks the parent directory first. Remote process limits are not separately controlled.

Test signals: parseable log lines include test name, file counts, memory/stack limits, and Unison exit status for initial and touch-all syncs.
