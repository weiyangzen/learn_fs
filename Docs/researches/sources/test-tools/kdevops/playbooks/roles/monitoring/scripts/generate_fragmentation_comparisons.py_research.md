<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/generate_fragmentation_comparisons.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/generate_fragmentation_comparisons.py

Purpose: orchestrates higher-quality fragmentation comparisons by selecting likely baseline/dev JSON pairs and invoking `fragmentation_visualizer.py` in compare mode.

Important APIs/types/functions: `find_first_matching_file()`, `generate_comparison()`, `main()`.

Control flow: `main()` scans a fragmentation results directory for filesystem-patterned files, picks first matching files, and calls `generate_comparison()` for ext4 versus XFS, baseline versus dev, and other named comparisons. `generate_comparison()` shells out to the visualizer with `--compare` and `-o`.

State and persistence behavior: Reads existing JSON files and writes comparison PNGs. It reports subprocess failures but does not change collected data.

Dependencies and integration points: Depends on Python subprocess execution, glob/path matching, and a valid visualizer path passed by `monitor_collect.yml`.

Risks: First-match selection can compare unintended hosts when multiple runs are present. Pair discovery is filename-convention-heavy. A visualizer failure surfaces only as comparison-generation output unless callers inspect return codes.

Test signals: Test with synthetic directories containing ext4/XFS/baseline/dev filenames, missing pair cases, explicit `--visualizer`, and command failure handling.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/generate_fragmentation_comparisons.py -->
