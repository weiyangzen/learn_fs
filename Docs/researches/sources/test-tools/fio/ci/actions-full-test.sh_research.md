## sources/test-tools/fio/ci/actions-full-test.sh

Purpose: runs fio's longer CI test lane and documentation build.

Important flow: `main()` exits early for Android builds, exports `PYTHONUNBUFFERED=TRUE`, builds a skip list for long tests that are unsuitable in CI (`6`, `1007`, `1008`, and `1018` because `null_blk` modules cannot be loaded), and adds debug mode. In `build-containers`, it additionally skips io_uring-heavy or command-priority-sensitive cases and overrides test `1021` to use `psync,libaio`. It then runs `python3 t/run-fio-tests.py -c` with the computed arguments and builds docs via `make -C doc html`.

State and persistence: it writes test artifacts/logs through the fio test runner and generated HTML under `doc`. It does not maintain its own state.

Dependencies and integration: depends on Python, SciPy/statsmodels/Sphinx packages installed by `actions-install.sh`, make, and the fio test suite under `t/`.

Risks and test signals: skip lists encode CI environment assumptions; if runners gain or lose capabilities the list can hide regressions or introduce false failures. The main signal is the Python test runner exit status plus documentation build success.
