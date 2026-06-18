<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_mmtests_graphs.py -->
# sources/test-tools/kdevops/scripts/generate_mmtests_graphs.py

Purpose: parses mmtests comparison output for `thpcompact`-style fault metrics and generates two PNG graphs plus an explanatory `graphs.html` report comparing baseline and development kernels.

Important APIs and functions: `parse_comparison_file()` extracts Amean rows for `fault-base`, `fault-huge`, and `fault-both`; `create_performance_comparison_graph()` writes `performance_comparison.png`; `create_detailed_thread_analysis()` writes `thread_analysis.png`; `generate_graphs_html()` writes an HTML report embedding both images; `main()` validates three CLI args and orchestrates parsing/rendering.

Control flow: check `comparison.txt`, output dir, and `baseline-dev` kernel name argument, create output dir, parse data, render summary graph, render thread analysis, render HTML, and print completion.

State and persistence: writes files under the supplied output directory. It uses matplotlib's `Agg` backend for headless operation.

Dependencies and integration: matplotlib, numpy, regex parsing, pathlib. It is referenced by mmtests CI/reporting flows.

Risks: the regex only matches decimal numeric values and specific `fault-*` names, so format changes or integer values are ignored. HTML includes a large static explanation with emoji/non-ASCII symbols. If parsed data is empty, graphs are still attempted and may produce low-value reports. Test signals include parser fixtures from real mmtests output, empty-data behavior, output file existence, and image smoke tests under headless CI.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_mmtests_graphs.py -->
