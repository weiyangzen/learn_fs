# sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/run.py

Purpose: core TestHarness2 orchestrator. It selects tests, chooses current/old binaries, runs `fdbserver`, handles buggify/restart/determinism/valgrind/long-running modes, records stats, decorates summaries, organizes determinism artifacts, and controls cleanup.

Important APIs/types: helpers `parse_test_args_file`, `binary_uses_sanitizers`, `resolve_fdbserver_memory`, predicates `is_restarting_test`/`is_negative`/`is_no_sim`/`is_rare`; classes `TestDescription`, `StatFetcher`, `TestPicker`, `OldBinaries`, `ResourceMonitor`, `TestRun`, and `TestRunner`.

Control flow: `TestPicker` scans configured test-type directories, parses `.txt/.toml` metadata, filters by regex, prioritizes rare tests, loads stats, and chooses least-runtime candidates. `TestRun.run()` builds the fdbserver command, optionally prefixes valgrind, sets TLS/memory/fault-injection/restart/buggify flags, runs with timeout, decodes output robustly, summarizes traces, and writes stdout capture. `TestRunner.run_tests()` handles restart sequences, optional unseed determinism reruns, Joshua logtool upload on failure, stats, and XML output.

State and persistence: creates per-UUID temp dirs under `config.run_temp_dir`; writes trace outputs, stdout, Valgrind XML, determinism analysis directories, README files, and maybe FDB stats/coverage through other modules. Cleanup deletes the UUID directory unless preserving failure logs.

Dependencies and integration: config singleton, `Version`, `Summary`, fdbserver binaries, old binary directory, Valgrind, `joshua_logtool.py`, FoundationDB trace naming, and OS resource accounting.

Risks and test signals: many environment-dependent branches; debug prints to stderr may affect failure classification; cleanup can remove artifacts unless archive env is set; `TestDescription.__eq__` appears to compare `<` instead of equality. Test direct args-file mode, restart binary selection, sanitizer memory auto-detection, decode errors, determinism failure organization, and logtool gating.
