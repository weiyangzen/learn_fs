## sources/sync-backup/rsync/testsuite/fleettest.py

Purpose: standalone fleet CI harness. It pushes a source-only rsync checkout to configured local or remote targets, builds it, runs the Python testsuite under pipe/TCP/older protocols/non-root modes, retries configured flakes, reports unexpected results, and cleans run remnants.

Important APIs and types: `Target`, `CmdResult`, `TransportResult`, and `TargetResult` dataclasses model target config and outcomes. Key functions include `load_fleet()`, `run_on()`, `push_argv()`, `parse_workflow_skip()`, `discover_nonroot_tests()`, `build_script()`, `test_script()`, `parse_transport()`, `retry_failed()`, `run_target()`, `print_report()`, `print_timing()`, `cleanup_run()`, `cleanup_remnants()`, and `main()`.

Control flow: `main()` parses CLI arguments, validates repo/testsuite, loads fleet JSON, optionally lists or cleans, assigns a random run id to build dirs, stages `git archive HEAD`, overlays an alternate testsuite when requested, discovers non-root tests, and runs targets concurrently. Each target is pinged, pushed with rsync, built, tested by selected transports and protocols, optionally non-root tested, then summarized.

State and persistence: reads fleet config and workflows, creates temporary staging dirs, remote build dirs, global cleanup target lists, and optional retained run dirs. Cleanup uses shell scripts with guarded patterns and `sudo -n` fallback.

Dependencies and integration: depends on ssh, rsync, git, tar, target toolchains, workflow skip lists, `runtests.py`, and target privilege model. It integrates with CI matrix semantics and tests marked `fleet_nonroot = True`.

Risks and test signals: high operational blast radius around remote `rm -rf` and process cleanup, mitigated by `_unsafe_builddir`, random suffixes, and scoped patterns. Signals are parsed PASS/FAIL/ERROR/SKIP counts, skip-list diffs, per-cell status, recovered flaky lists, and timing summaries.
