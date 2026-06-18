# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigCP.cc

## Purpose

`XrdOfsConfigCP.cc` implements configuration and startup recovery for OFS checkpoint files. It owns the static checkpoint settings, parses the `ofs.chkpnt` directive, initializes the checkpoint directory, restores outstanding `.ckp` files, reports unresolved `.ckperr` failures, and disables checkpointing for unsafe default `/tmp` paths unless explicitly enabled.

## Important APIs, Types, and Functions

- Static settings: `Path`, `MaxSZ`, `MaxVZ`, `cprErrNA`, `Enabled`, `isProxy`, and `EnForce`.
- `Init()` resolves the checkpoint directory, creates it, rejects or warns about `/tmp`, scans files with `XrdOucNSWalk`, calls `Recover()` for each entry, reports restore counts, and finalizes enablement.
- `Parse()` handles `disable`, `enable`, `cprerr`, `maxsz`, and `path` options for the `chkpnt` directive.
- Private `Stats` counts files, recovered checkpoints, errors, skipped entries, and unresolved error files.
- `Recover()` classifies `.ckperr`, `.ckp`, and unknown files; unresolved errors are reported with `XrdOfsCPFile::Target()`, valid checkpoints are restored through `XrdOfsChkPnt`.

## Control Flow

During OFS configure, non-manager non-proxy servers call `XrdOfsConfigCP::Init()`. If checkpointing is disabled or proxy mode is set, initialization returns success without work. Otherwise, `Path` is either derived from a configured absolute path plus instance/chkpnt suffix or from `XRDADMINPATH/chkpnt/`. The directory is created, scanned, and each file is recovered or reported. If the resolved path is rooted in `/tmp/` and the user did not explicitly `enable`, checkpointing is auto-disabled after recovery.

`Parse()` is invoked from `XrdOfs::ConfigXeq()` for `ofs.chkpnt`. It updates static settings as tokens are read.

## State and Persistence Behavior

Checkpoint state is persisted as files in `Path`. On startup, `.ckp` files are treated as recoverable in-progress checkpoints and are applied to their target files. `.ckperr` files are treated as unresolved restore failures requiring operator attention. Other files are skipped with a warning. `MaxSZ` limits per-checkpoint saved data during runtime, and `cprErrNA` controls whether restore failures make the source inaccessible or read-only.

## Dependencies and Integration Points

This file depends on global `XrdOfsOss` to allocate recovery file objects, global `OfsEroute` for logging, `XrdOfsChkPnt` for actual restore, `XrdOfsCPFile::Target()` for unresolved error reporting, `XrdOuca2x` for size parsing, `XrdOucUtils` for path construction/creation, `XrdOucNSWalk` for directory scans, and `XrdOucString` for normalized path strings.

## Risks and Edge Cases

- In `Parse()`, the `cprerr` branch compares the current token `val` to `makero`/`stopio` without first reading the option token after `cprerr`; as written, `ofs.chkpnt cprerr makero` appears to fail. This should be tested or corrected.
- `Recover()` does not check whether `XrdOfsOss->newFile("checkpoint")` returns null before constructing `XrdOfsChkPnt`.
- `MaxVZ` is declared and initialized but not used in this file or the visible checkpoint implementation.
- `/tmp` auto-disable happens after scanning/recovery; explicit `enable` only warns.
- `Path` construction differs depending on whether `Path` was explicitly configured; configured paths get instance plus `chkpnt/` appended by `Init()`, even though `Parse()` already ensures a trailing slash.

## Test Signals

Tests should cover default path resolution with and without `XRDADMINPATH`, absolute path parsing and normalization, `/tmp` auto-disable versus explicit enable, directory creation failure, scan failure, recovery of valid `.ckp`, unresolved `.ckperr`, skipped unknown files, restore failure counts, and all parser options including the suspected `cprerr` token bug.
