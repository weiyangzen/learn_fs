# sources/test-tools/kdevops/playbooks/fio-tests-multi-fs-compare.yml

Purpose: compares fio-test results across multiple filesystem configurations and writes multi-filesystem analysis artifacts.

Important APIs/types/functions: localhost play with variables `results_dir`, `output_dir`, `python_path`, and `comparison_script`. Uses `stat`, `fail`, `find`, `set_fact`, `pip`, `shell`, `find`, `template`, and `debug`.

Control flow: validate results directory and comparison script, find JSON result files recursively, extract filesystem configuration names from paths, require at least two configurations, optionally install plotting packages, run `fio-multi-fs-compare.py`, list generated files, template a summary, and print final status.

State/persistence behavior: writes multi-filesystem comparison plots and summaries under `<results_dir>/multi-fs-comparison`.

Dependencies/integration: consumes fio result JSONs from filesystem-matrix runs and depends on the Python comparison script plus plotting stack.

Risks/test signals: filesystem configuration extraction from paths is convention-sensitive. Installing packages with `pip` can modify the controller environment. Test signals are failure on zero/one config, generated plots, and a templated summary with total config/file counts.
