<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/contrib_graph.py -->
# sources/test-tools/kdevops/scripts/contrib_graph.py

Purpose: generates contribution visualizations from the current git repository, writing PNG and PDF reports under `docs/contrib/`. It accepts optional `--year`, optional `--month`, and `--show`, then analyzes git history for contributor totals, month-level commit counts, and `Generated-by:` tag adoption.

Important APIs and functions: `run_git_command()` shells out to git with `shell=True`; `get_date_range()` computes bounded date filters; `get_contribution_data()` runs several `git log` pipelines and returns contributor totals, monthly data, total commits, period text, an AI-boom marker, and generated-by monthly counts; `create_contribution_graphs()` builds a multi-panel matplotlib/seaborn figure; `main()` validates CLI dates and repository context.

Control flow: CLI validation happens first, then git repository detection, contribution data extraction, plotting, optional display, and completion logging. The plotting function builds seven views: contributor bar chart, pie chart, activity heatmap, monthly timeline, top-contributor timeline, text statistics, and generated-by adoption trend.

State and persistence: reads only git history but writes `docs/contrib/kdevops_contributions_*.png` and `.pdf`, creating the directory if needed. It depends on current system time when bounding current-year plots and embedding generation timestamps.

Dependencies and integration: depends on git, matplotlib, numpy, pandas, and seaborn. It is a standalone reporting tool, likely run from the kdevops repo root.

Risks: `run_git_command()` uses shell strings, so internal command construction must remain trusted. Monthly aggregation keys only by month number, so all-time mode collapses the same month across different years in some charts. Git author names are used directly in labels. Large histories may be slow. Test signals include running in a small temporary git repo with known commits, checking output file creation, and unit testing date range and parser behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/contrib_graph.py -->
