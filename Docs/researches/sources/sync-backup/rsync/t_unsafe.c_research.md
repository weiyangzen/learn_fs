<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/t_unsafe.c -->
# sources/sync-backup/rsync/t_unsafe.c

Purpose: tiny standalone test harness for rsync's `unsafe_symlink()` helper.

Important APIs/types/functions: `main()` only, plus minimal rsync globals required for linking.

Control flow: require exactly `LINKDEST` and `SRCDIR` arguments, call `unsafe_symlink(argv[1], argv[2])`, print `unsafe` or `safe`, and return 0 unless usage is wrong.

State and persistence behavior: read-only; no filesystem mutation is performed by this harness.

Dependencies and integration points: links against rsync code that implements `unsafe_symlink()`. Used by shell tests to classify symlink targets under rsync's safe-links logic.

Risks: the harness exposes only a binary textual result and does not assert expected values itself. It sets `am_sender=1`, which matters for code paths that depend on sender/receiver role.

Test signals: shell-level fixtures pass link targets and source dirs and compare stdout to expected `safe` or `unsafe`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/t_unsafe.c -->
