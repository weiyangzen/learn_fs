## sources/test-tools/xfstests/common/gcov

Purpose: this library captures kernel gcov data after fstests runs and optionally generates lcov/genhtml reports.

Important APIs: `__gcov_find_topdirs` finds the shallowest directories under `/sys/kernel/debug/gcov` that contain `.gcno` files. `_gcov_generate_report output_dir` copies raw gcov source directories, runs `lcov --capture`, optionally runs `genhtml`, and optionally renders `index.html` to text using `lynx`, `links`, or `elinks`. `_gcov_reset` writes `1` to the gcov reset knob. `_gcov_check_report_gcov` disables `REPORT_GCOV` if the running kernel does not expose a writable reset knob.

Control flow: report generation is entirely conditional. It returns immediately if no output directory was requested, kernel gcov support is absent, no `.gcno` directories exist, or `lcov` is unavailable. If supported, it copies `/sys/kernel/debug/gcov/*` into `raw/`, builds an lcov command with every top gcno directory, prepares optional HTML/text commands, and runs them with stdout/stderr captured under the output directory.

State and persistence: raw gcov trees are persisted under `<output_dir>/raw/`, the summary is `<output_dir>/gcov.report`, command logs are `gcov.stdout` and `gcov.stderr`, generated HTML lives under `output_dir`, and `index.txt` may be created. `_gcov_reset` mutates kernel coverage counters.

Dependencies and integration: it depends on debugfs gcov at `$GCOV_DIR`, `find`, `sort`, `uniq`, `$AWK_PROG`, `cp`, `lcov`, and optionally `genhtml` and terminal web browsers. `fstests_start_time` is used to title reports when available.

Risks: copying the full gcov tree can consume disk space and time. The topdir finder assumes the shallowest `.gcno` hierarchy is the desired lcov directory set. Missing optional tools silently reduce output. `_gcov_reset` does not guard against missing write permission; callers should use `_gcov_check_report_gcov`.

Test signals: the primary signals are non-empty `gcov.report`, successful `gcov.stdout`, lack of fatal messages in `gcov.stderr`, and optional `index.txt` with coverage summaries. If `REPORT_GCOV` is unset after checking, the kernel or permissions do not support collection.
