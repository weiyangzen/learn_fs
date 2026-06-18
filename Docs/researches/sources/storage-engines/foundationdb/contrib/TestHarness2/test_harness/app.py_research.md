# sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/app.py

Purpose: primary TestHarness2 CLI entrypoint. It builds config from CLI/env, sets up logging, runs `TestRunner`, and ensures Joshua receives XML on ordinary failure, exception, or abnormal early termination.

Important APIs/functions: `setup_logging()` writes `app_log.txt` under `config.run_temp_dir` or `/tmp`; `create_error_xml()` constructs a `SummaryTree("Test")` with `Ok="0"` and a `JoshuaMessage`; the module main block wires argparse, config extraction, `TestRunner().run()`, and fallback XML.

Control flow: parse args, configure logging, run tests, exit 1 on false success, catch exceptions into fatal XML, and in `finally` emit emergency fallback XML if nothing was generated.

State and persistence: writes a log file and stdout XML/JSON summaries. It depends on global mutable `config`.

Dependencies and integration: imports `test_harness.config`, `run.TestRunner`, and `summarize.SummaryTree`; called by Joshua wrapper scripts.

Risks and test signals: `create_error_xml` returns a `SummaryTree` despite type hint `str`; logger setup occurs after config parsing, so config parse failures bypass file logging. Test with missing required `--run-temp-dir`, runner exceptions, and normal failed tests.
