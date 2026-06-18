# sources/test-tools/kdevops/playbooks/python/workflows/blktests/gen-results-dir.py

Purpose: copies the latest blktests run into a kernel-named result directory and optionally trims it to only failed tests and companion files.

Important APIs/types/functions: globals define `results_dir`, `last_run_dir`, and `blktests_last_kernel`. Functions are `clean_empty_dir` and `main`. Uses `copytree`, `rmtree`, `glob`, `os.walk`, and `argparse` options `--clean-dir-only` and `--copy-all`.

Control flow: read last kernel, optionally only prune empty directories, copy `last-run` to `<results>/<kernel>/`, remove files for tests that have no `.bad` or `.dmesg` companion unless `--copy-all` is set, then recursively remove empty directories.

State/persistence behavior: writes/prunes workflow result directories under `workflows/blktests/results`.

Dependencies/integration: supports curating blktests failure artifacts for baselines and expunge generation.

Risks/test signals: references `line` after the kernel read loop, which is fragile for empty files; recursive pruning can be expensive and deletion-heavy. Test signals are kernel-named result directory creation, retained failed tests, removed passing-only files, and no empty directories after cleanup.
