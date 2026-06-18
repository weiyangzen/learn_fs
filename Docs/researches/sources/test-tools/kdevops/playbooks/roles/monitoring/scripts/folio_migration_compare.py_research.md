<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/folio_migration_compare.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/folio_migration_compare.py

Purpose: creates localhost comparison plots for folio migration stats collected from multiple kdevops hosts or filesystem configurations.

Important APIs/types/functions: `parse_stats_file()`, `get_node_label()`, `generate_comparison_plot()`, `generate_all_comparisons()`, `main()`.

Control flow: `generate_all_comparisons()` searches a monitoring result tree for `*_folio_migration_stats*.txt`, groups them into all-host and baseline/dev comparisons, then `generate_comparison_plot()` parses cumulative success counters and writes PNG charts.

State and persistence behavior: Reads copied text stats and writes `folio_migration_comparison*.png` artifacts in the monitoring results directory. It keeps only transient parsed series in memory.

Dependencies and integration points: Depends on matplotlib, numpy, regex parsing of debugfs-style migrate_folio stats, and `visualize.yml` or interim collection tasks.

Risks: Parsing assumes `calls` and `success` lines in each timestamped block. Filename-derived labels can misclassify new workflow naming. Missing or sparse files produce skipped plots.

Test signals: Signals include successful parsing of several timestamp formats, generated all-host and A/B plots, empty-directory no-op behavior, and labels matching baseline/dev host names.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/folio_migration_compare.py -->
