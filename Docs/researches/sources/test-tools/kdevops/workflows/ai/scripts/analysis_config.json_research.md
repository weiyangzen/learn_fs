# sources/test-tools/kdevops/workflows/ai/scripts/analysis_config.json

Purpose: default JSON configuration for AI benchmark result analysis and graph generation.

The schema contains `enable_graphing`, `graph_format`, `graph_dpi`, and `graph_theme`. `analyze_results.py` loads this file when passed via `--config` and overlays it onto its built-in defaults.

There is no control flow or persistence beyond static JSON. Integration points are Ansible result-analysis tasks or manual invocations of `workflows/ai/scripts/analyze_results.py`.

Risks are low, but the configured DPI of 150 differs from the script's built-in default of 300, so output quality depends on whether the config file is supplied. Unsupported `graph_format` or invalid matplotlib style names are not validated here. Test signals should parse JSON, verify keys and types, run analyzer with this config on a small fixture, and confirm graph filenames use the configured extension and DPI path without errors.
