<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/files/plot_migration_stats.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/files/plot_migration_stats.py

Purpose: renders detailed folio migration time-series plots from timestamped debugfs `migrate_folio` stats, including cumulative calls/success, interval rates, and trimmed workload activity windows.

Important APIs/types/functions: `human_format()`, `parse_stats_file()`, `find_start_index()`, `cumulative_to_interval()`, `find_end_of_activity()`, `plot_folio_migration()`, `main()`.

Control flow: `parse_stats_file()` extracts timestamp blocks and `calls`/`success`; `cumulative_to_interval()` converts counters; `find_end_of_activity()` trims trailing idle periods; `plot_folio_migration()` builds one-file, A/B, or comprehensive plots with paired baseline/dev styling; `main()` parses inputs and output path.

State and persistence behavior: Reads stats text and writes matplotlib PNGs. It persists no host state and uses only derived in-memory series.

Dependencies and integration points: Used by folio migration collect and collect-only tasks. Depends on matplotlib and timestamp/stat text generated from `/sys/kernel/debug/mm/migrate_folio_stats`.

Risks: Counter resets or missing timestamp blocks can produce negative or sparse intervals. Activity trimming assumes minute cadence. Very large file sets may crowd legends and labels.

Test signals: Validate ISO and syslog timestamp parsing, cumulative-to-interval conversion, idle-tail trimming, two-file A/B plots, multi-host plots, and output creation with empty data handled predictably.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/files/plot_migration_stats.py -->
