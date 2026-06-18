
# sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_fs_ng.c

## Purpose

`recovery_fs_ng.c` implements a newer filesystem recovery backend that keeps the legacy per-client directory record format but changes how recovery epochs are managed. Instead of maintaining separate current and old directories directly, it creates a fresh temp directory for this boot and swaps a stable host/node symlink to the new directory at end of grace.

## Important APIs, types, and functions

- `v4_recov_link` is the stable symlink path, usually `<recov_root>/<recov_dir>/<hostname>` or `node%d`.
- `legacy_fs_db_migrate()` detects an old backend directory at the link path, renames it to a temp sibling, and replaces it with a symlink so fs-ng can recover legacy state.
- `fs_ng_create_recov_dir()` creates root/base directories, derives host or node id, creates a fresh `mkdtemp()` active directory, updates `v4_recov_dir`, and runs migration.
- `fs_ng_read_recov_clids_impl()` recursively reads the symlink target directory and reconstructs legacy client tags.
- `fs_ng_read_recov_clids()` is the backend read hook. Normal local recovery is implemented; takeover code is currently compiled out behind `#ifndef FIXME` early return.
- `fs_ng_swap_recov_dir()` atomically installs a temporary symlink pointing at the new active directory and removes the old real directory after the rename.
- `fs_ng_backend` reuses `fs_add_clid()`, `fs_rm_clid()`, and `fs_add_revoke_fh()` from the legacy filesystem backend.

## Control flow

Initialization creates `<root>/<recov_dir>`, chooses a stable identity from `g_nodeid` or `gethostname()`, builds `v4_recov_link`, and creates `v4_recov_dir` as `<link>.XXXXXX` via `mkdtemp()`. The legacy migration step runs after the new temp directory exists so an old directory at the stable link path can be renamed and linked without losing recoverable state.

During normal restart, `fs_ng_read_recov_clids_recover()` reads `v4_recov_link`, not the fresh active directory, because the link points to the previous epoch's durable records. It reconstructs client names with the same `<IP>-(len:value)` validation used by the legacy backend and adds each valid leaf with `reclaim_complete=true`.

At end of grace, `fs_ng_swap_recov_dir()` captures the old realpath, creates `<link>.tmp` pointing to `basename(v4_recov_dir)`, renames the temporary symlink over `v4_recov_link`, and then recursively deletes the old target directory.

## State and persistence behavior

The stable durable state is a symlink whose target is a generation directory. Active records for the current process are written to the fresh temp directory through reused `fs_add_clid()` helpers. The symlink is not updated until grace ends, so crashes during grace leave the previous generation visible for the next process.

Revoked handle and client directory formats remain identical to `recovery_fs.c`, but this reader does not import revoke handle files despite accepting an `add_rfh_entry` hook; it currently only adds client entries.

## Dependencies and integration points

The backend depends on `recovery_fs.h` for shared globals and record helpers, POSIX `mkdtemp`, `symlink`, `rename`, `realpath`, and `basename`, and the generic recovery backend table. It integrates with existing filesystem record generation while changing the epoch switch primitive to symlink replacement.

## Risks and edge cases

- Takeover support is effectively disabled by an unconditional `return` in the `gsp` path. Cluster/failover operators need a different backend or completed implementation.
- `legacy_fs_db_migrate()` is explicitly non-atomic; a crash between rename and symlink creation can strand old records.
- `fs_ng_read_recov_clids_impl()` ignores revoke files and always marks clients reclaim-complete, which differs from legacy marker semantics.
- Symlink cleanup depends on `realpath(v4_recov_link)` before replacement. If the link is missing or invalid, old generation cleanup is skipped.
- Reused legacy helpers depend on `v4_recov_dir` pointing to the temp generation, so initialization order is critical.

## Test signals

Test symlink swap atomicity, restart before end grace, restart after end grace, migration from a legacy directory, missing/broken symlink behavior, host and node naming, long client path reconstruction, and the disabled takeover path. Tests should confirm that new client records are written to the temp directory and become visible only after `end_grace`.
