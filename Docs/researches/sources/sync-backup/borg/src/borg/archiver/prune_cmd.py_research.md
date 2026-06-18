# sources/sync-backup/borg/src/borg/archiver/prune_cmd.py

## Purpose

`prune_cmd.py` implements `borg prune`, applying retention rules to archive sets and soft-deleting archives that are not retained. It supports keep-within and GFS-style time bucket retention at second, minute, hour, day, week, month, quarter, and year granularities. The source was read as a complete 420-line file.

## Important APIs, Types, and Functions

Pure helper functions include `prune_within()`, `default_period_func()`, `quarterly_13weekly_period_func()`, `quarterly_3monthly_period_func()`, and `prune_split()`. `PRUNING_PATTERNS` orders retention buckets. `PruneMixIn.do_prune()` validates that at least one retention rule is set, selects archive format, builds an `ArchiveFormatter`, resolves matching archives while excluding `@PROT`, computes keep/delete sets, logs or emits JSON, deletes unkept archive IDs, writes the manifest, and handles SIGINT. `build_parser_prune()` wires retention flags, list/format/json options, archive filters, and optional name.

## Control Flow

The command first rejects invocations with no retention rule. It selects a display format, resolves a candidate archive list sorted newest-first, and filters protected archives. It creates `keep` and `kept_because`, adds all archives newer than `--keep-within`, then iterates `PRUNING_PATTERNS` in order and calls `prune_split()` for each configured count. `prune_split()` keeps the newest archive per period, avoids archives already kept by earlier rules, and keeps the oldest archive if the requested count cannot be reached. The complement is soft-deleted unless dry-run. Output can include all archives, only pruned, only kept, or JSON.

## State and Persistence Behavior

Like `delete`, prune only mutates manifest archive metadata by soft-deleting archive entries. It does not free repository object storage and prints a compact reminder after actual deletions. Dry-run computes and reports without writing. JSON output is generated before manifest write and includes kept/deleted metadata. SIGINT can break the deletion loop and then raises `Error`.

## Dependencies and Integration Points

The module depends on manifest archive listing/deletion, archive filters, `ArchiveFormatter`, `interval()` parsing, progress display, JSON helpers, and global `sig_int`. It is coupled to `compact_cmd.py` for final object cleanup and to help text documenting GFS retention semantics.

## Risks and Edge Cases

Without a name or match pattern, all non-protected archives are candidates; the epilog warns users to run one prune per series. Local timezone is used for period grouping, including ISO week semantics. Negative keep counts are accepted by argparse as ints, but `prune_split()` breaks only when `len(keep) == n`; negative values effectively have no equality target and can keep every period. Sorting and set conversion require archive info objects to be hashable and comparable by identity/value as expected.

## Test Signals

Tests should cover each retention granularity, both quarterly strategies, `--keep-within`, earlier-rule precedence, oldest-retention fallback, dry-run, protected tags, JSON output fields, list-kept/list-pruned/list behavior, no-rule rejection, name versus match filtering, negative keep semantics, SIGINT interruption, and manifest write only when archives are actually deleted.
