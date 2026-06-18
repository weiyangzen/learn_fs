<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/fragmentation_ab_compare.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/fragmentation_ab_compare.py

Purpose: generates multi-panel A/B comparison plots for fragmentation tracker output, emphasizing extfrag counts, migration pages, compaction success, fragmentation index, and migration-focused summaries.

Important APIs/types/functions: `load_fragmentation_data()`, `extract_all_metrics()`, `get_node_label()`, `generate_ab_comparison()`, `generate_migration_focus_plot()`, `generate_all_comparisons()`, `main()`.

Control flow: Loads JSON event lists, bins activity into 60-second windows in `extract_all_metrics()`, derives labels from filenames, and builds comprehensive or migration-focused matplotlib figures. `generate_all_comparisons()` scans monitoring results and emits all-data and pairwise comparison plots.

State and persistence behavior: Purely derived output: reads `*_fragmentation_data*.json` and writes PNG comparison files. No target state is changed.

Dependencies and integration points: Depends on matplotlib, numpy, and tracker JSON. Integrated from `visualize.yml` and complements the richer `fragmentation_visualizer.py` comparison mode.

Risks: The metric extractor expects event types such as `migration` and `compaction` that are not always produced by the current tracker, so some panels can be empty for extfrag-only runs. Labeling and color assignment depend on filename conventions.

Test signals: Exercise extfrag-only JSON, mixed migration/compaction JSON, two-file pair comparisons, multi-file comparisons, parse failures, and generated output existence.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/fragmentation_ab_compare.py -->
