<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/fragmentation_compare.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/fragmentation_compare.py

Purpose: legacy/simple fragmentation comparison script. It extracts extfrag event counts over time and delegates users toward `fragmentation_ab_compare.py` for richer analysis.

Important APIs/types/functions: `load_fragmentation_data()`, `extract_fragmentation_metrics()`, `get_node_label()`, `generate_comparison_plot()`, `generate_all_comparisons()`, `main()`.

Control flow: `generate_all_comparisons()` finds fragmentation JSON files, `extract_fragmentation_metrics()` filters external fragmentation events into time/count arrays, and `generate_comparison_plot()` can render line graphs though the code marks it deprecated.

State and persistence behavior: Reads JSON and writes comparison PNGs under the monitoring results tree. It does not modify source data.

Dependencies and integration points: Depends on matplotlib, numpy, JSON output from the tracker, and `visualize.yml` still invokes it before the A/B script.

Risks: The line graph is explicitly described as not very useful, and it only reflects extfrag event occurrence rather than severity or migratetype transitions. Bad JSON is skipped with a warning.

Test signals: Validate no-op behavior with no files, parse warnings for malformed JSON, and plot output for multiple non-empty fragmentation data files.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/fragmentation_compare.py -->
