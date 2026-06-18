# sources/test-tools/kdevops/playbooks/fio-tests-graph.yml

Purpose: top-level fio-test graph generator that processes each host result directory and optionally creates combined cross-host graphs.

Important APIs/types/functions: localhost play with facts, variables `results_base_dir`, `python_path`, and `fio_plot_script`. Uses `stat`, `fail`, `find`, `include_tasks: fio-tests-graph-host.yml`, `file`, `shell`, and `debug`.

Control flow: verify result directory, discover host directories, include per-host graph tasks for each, then when more than one host exists create a combined graph directory, aggregate JSONs with hard links into a temporary directory, run the plotter for combined comparison, clean up, and print summary.

State/persistence behavior: writes per-host graph directories and a combined graph directory under `workflows/fio-tests/results`.

Dependencies/integration: depends on `fio-tests-graph-host.yml`, `fio-plot.py`, result directory conventions, and Python plotting libraries.

Risks/test signals: hard-link aggregation can fail across filesystems; result naming collisions can occur in combined temp directories. Test signals are per-host PNGs, combined PNGs when multiple hosts exist, and cleanup of temporary aggregation directory.
