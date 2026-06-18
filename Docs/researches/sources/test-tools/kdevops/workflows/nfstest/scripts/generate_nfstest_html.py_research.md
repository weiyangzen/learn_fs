## sources/test-tools/kdevops/workflows/nfstest/scripts/generate_nfstest_html.py

Purpose: Generates an HTML visualization for parsed nfstest results, with summary cards, progress bars, per-suite tables, optional charts, and configuration display.

Important APIs/types/functions: Functions include `format_time`, `generate_suite_chart`, `generate_overall_chart`, `embed_image`, `generate_html`, and `main`. `HTML_TEMPLATE` contains the page structure and styling.

Control flow: `main` takes a results directory or defaults to `workflows/nfstest/results/last-run`, requires `parsed_results.json`, creates a sibling `html` directory, loads parsed JSON, and calls `generate_html`. The generator computes overall stats, optionally produces matplotlib charts, embeds PNGs as base64, builds expandable suite sections, and writes `index.html`.

State and persistence: Reads `parsed_results.json`; writes chart PNGs and `index.html` under the generated html directory.

Dependencies and integration points: Depends on a separate parser (`parse_nfstest_results.py`) producing the expected JSON schema. Matplotlib is optional; without it the HTML still renders without charts.

Risks and test signals: The template contains decorative Unicode and some CSS brace irregularities, but the bigger functional risk is schema drift in `parsed_results.json`. Test with parser output containing passed/failed suites, no-result suites, and no matplotlib installed.
