# sources/test-tools/kdevops/playbooks/fio-tests-graph-host.yml

Purpose: task include that processes fio-test results for one host and generates host-specific performance graphs.

Important APIs/types/functions: expects variables `host_name`, `host_results_dir`, `python_path`, and `fio_plot_script`. Uses `find`, `debug`, `file`, shell import check for `pandas`, `matplotlib`, `numpy`, and `seaborn`, package installation with become, graph generation shell command, and graph discovery.

Control flow: find `results_*.json`, skip gracefully if none, create `graphs`, ensure plotting dependencies, run `fio-plot.py`, then list generated PNG files.

State/persistence behavior: creates `graphs/` under the host result directory and may install Python plotting packages system-wide.

Dependencies/integration: included by `fio-tests-graph.yml` once per host directory.

Risks/test signals: package names are distro-specific and the dependency check is `run_once`, so mixed hosts can be undervalidated. Test signals are generated PNGs with prefix `<host>_performance` and no failure for empty host result directories.
