# sources/sync-backup/bup/lib/bup/cmd/prune_older.py

## Purpose
`prune_older.py` removes old saves according to retention windows and optionally runs garbage collection afterward. It is experimental and requires `--unsafe`.

## APIs and Control Flow
`branches` yields selected head names and hashes. `classify_saves` assumes decreasing UTC order and retains all saves in the newest window, then the newest save per day/month/year for configured windows, then drops older saves. `main(argv)` parses retention periods relative to `--wrt` or current time, logs effective windows, enumerates branch revisions with author times, derives save names using `save_names_for_commit_utcs`, prints intended actions under `--pretend`, or calls `bup_rm` and then `bup_gc`.

## State, Dependencies, Integration, Risks, Tests
Persistent effects are ref/history rewrites via `bup_rm` and pack cleanup via `bup_gc`. Dependencies include `git.rev_list`, `period_as_secs`, `partition`, `LocalRepo`, `bup_rm`, and `bup_gc`. Risks include dangerous experimental deletion, memory use from building full rev lists, reliance on save-name derivation rather than hashes, timezone/localtime grouping, and retention window edge cases. Test signals include `--unsafe` gate, period parsing, `--pretend` output, classification ordering, branch filters, error gating via `die_if_errors`, and optional GC invocation.
