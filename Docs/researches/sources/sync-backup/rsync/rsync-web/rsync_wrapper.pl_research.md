# sources/sync-backup/rsync/rsync-web/rsync_wrapper.pl

Purpose: Legacy Perl module `Rsync` that wraps the external rsync binary with object-oriented option storage, execution, and accessors for stdout/stderr/status.

Important APIs, types, and functions: `new()` creates an object with default path `/usr/local/bin/rsync`, recognized boolean/scalar option hashes, ordered exclude/include data, source/destination data, debug flag, output arrays, and status fields. `defopts()` parses short/long/default options into the object. `exec()` builds the command, runs it via `IPC::Open3::open3`, captures stdout/stderr, waits, and stores shifted and raw statuses. Accessors are `status()`, `realstatus()`, `err()`, and `out()`.

Control flow: Options passed to `new()` or `defopts()` are normalized from short to long form, with special handling for scalar short options `-B`, `-e`, `-T`, `--exclude`, `--include`, reset marker `!`, and `--path-to-rsync`. `exec()` sorts flag/scalar option keys, appends excludes, stored data, and per-call args, then launches rsync.

State and persistence behavior: Object state persists defaults and last-run outputs/status. Per-call args are not saved. The wrapper does not persist files itself, but rsync side effects are whatever command arguments request.

Dependencies and integration points: Depends on Perl 5.004, `FileHandle`, `IPC::Open3`, and `Carp`. Integrates as a convenience API for website/legacy automation around rsync.

Risks and test signals: Risks include deadlock potential from reading stderr fully before stdout if a child writes enough stdout, sorted option ordering changing semantic order for some options, stale option list relative to modern rsync, and shell-free but user-controlled binary path execution. Tests should cover option parsing, include/exclude ordering, failure to exec, large stdout/stderr, status accessors, and custom rsync path.
