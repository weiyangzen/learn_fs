# sources/test-tools/kdevops/playbooks/python/workflows/fstests/bad_files_summary.py

Purpose: Produces a simple text or HTML summary of fstests `.bad` files grouped by section for a filesystem.

Key APIs and flow: `main()` walks the result directory, filters `.bad` files, derives kernel, section, test type, and test number from positional path segments, stores `test_type/test_number` entries per section, then dispatches to `parse_results_ascii()` or `parse_results_html()`.

State, dependencies, integration: Reads result files but writes only to stdout. Depends on Python stdlib and expected kdevops fstests path layout such as `results/oscheck-xfs/<kernel>/<fs>/<group>/<test>.out.bad`.

Risks and test signals: HTML is manually concatenated without escaping and has table nesting quirks; kernel is whichever bad file was seen last; positional parsing fails on unexpected layouts. Tests should cover no failures, multiple sections, HTML output, filenames with extra dots, and special characters in section names.
