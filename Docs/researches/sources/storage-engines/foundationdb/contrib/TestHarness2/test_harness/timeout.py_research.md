# sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/timeout.py

Purpose: converts leftover trace artifacts from timed-out Joshua jobs into killed-test summaries.

Important APIs/functions: `files_matching`, `dirs_with_files_matching`, and main CLI. It builds config args, optionally finds Valgrind XML, then recursively finds directories containing `trace.*.(json|xml)`.

Control flow: for each trace timestamp group in each directory, construct `Summary(Path("bin/fdbserver"), was_killed=True, long_running=config.long_running)`, attach Valgrind XML when requested, summarize files, and dump stdout.

State and persistence: no writes; reads current working directory recursively.

Dependencies and integration: config, `Summary`, `TraceFiles`, regex, pathlib. Called by Joshua timeout shell wrappers.

Risks and test signals: recursive scan may include stale artifacts; Valgrind mode pairs every Valgrind file with every trace group. Test with nested trace dirs, no traces, long-running flag, and Valgrind XML parse errors.
