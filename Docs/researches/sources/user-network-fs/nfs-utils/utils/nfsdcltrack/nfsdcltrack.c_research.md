<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/nfsdcltrack.c -->
# sources/user-network-fs/nfs-utils/utils/nfsdcltrack/nfsdcltrack.c

## Purpose

`nfsdcltrack.c` implements the older command-style NFSv4 client tracking helper invoked by the kernel. It decodes hex client IDs, updates an SQLite database, supports reclaim checks and grace completion, and bridges legacy recovery-directory state.

## Important APIs, types, and functions

Commands are described by `struct cltrack_cmd`: `init`, `create`, `remove`, `check`, and `gracedone`. Helpers include `hex_to_bin`, `hex_str_to_bin`, `cltrack_set_caps`, `cltrack_lift_grace_period`, `cltrack_get_grace_start`, `cltrack_reclaims_complete`, `cltrack_client_has_session`, command handlers, legacy check/cleanup helpers, config reading, and `main`.

## Control flow

`main` reads config, parses debug/foreground/storage options, opens logging, drops capabilities, locates the requested command, validates required arguments, and invokes the command handler. `init` prepares SQLite and may lift grace if all reclaims are complete. `create`, `remove`, and `check` decode the hex client ID into a binary blob, then call SQLite. `check` falls back to a legacy recovery directory environment variable if the DB lookup fails. `gracedone` parses a grace start time, deletes unreclaimed records, and cleans legacy directories.

## State and persistence behavior

Persistent state is `main.sqlite` under the configured storage directory, with a `clients` table storing client ID blobs, timestamps, and `has_session`. The helper also writes `Y` to `/proc/fs/nfsd/v4_end_grace` to lift grace when conditions allow. Legacy directory cleanup uses environment-provided paths from the kernel.

## Dependencies and integration points

It depends on kernel-provided command-line arguments and environment variables (`NFSDCLTRACK_GRACE_START`, `NFSDCLTRACK_CLIENT_HAS_SESSION`, legacy paths), SQLite backend, libcap, config parsing, xlog, and procfs end-grace control.

## Risks and edge cases

`hex_str_to_bin` can partially clobber the destination before reporting `-ENOBUFS`. Capability dropping occurs before database access, so storage ownership matters. Invalid or missing grace-start env vars prevent early grace lifting. Legacy check removes recovery directories after inserting records, so failures can leave duplicate recovery sources.

## Test signals

Tests should cover each command, invalid commands returning `-ENOSYS`, missing arguments, odd/non-hex/too-long client IDs, storage permission cases, session and grace env vars, legacy fallback success/failure, grace lifting, unreclaimed pruning, and foreground/syslog behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/nfsdcltrack.c -->
