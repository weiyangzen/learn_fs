# sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/config.py

Purpose: central configuration registry for TestHarness2, exposing every option as a mutable global `config` value with argparse and environment-variable support.

Important APIs/types: `BuggifyOptionValue`, `BuggifyOption`, `ConfigValue`, and `Config`. Main methods are `change_default`, `build_arguments`, `extract_args`, `_build_map`, `_read_env`, and `_parse_env_value`.

Control flow: `Config.__init__` declares defaults and `<name>_args` metadata, builds an ordered map by reflecting attributes, reads env defaults, and seeds `random` from `joshua_seed`. `build_arguments` emits argparse flags; `extract_args` writes parsed values back to the singleton and reseeds.

State and persistence: all harness modules read shared in-memory singleton state. It also defines paths and Joshua/FDB integration settings, but persists nothing directly.

Dependencies and integration: Python argparse/env, `Path`, random, and every TestHarness2 module. Joshua wrappers map env vars such as `JOSHUA_SEED`, `JOSHUA_TEST_FILES_DIR`, and `TH_ARCHIVE_LOGS_ON_FAILURE` into this layer.

Risks and test signals: reflection order and `_args` placement are fragile; bool env parsing is strict; `BuggifyOption` invalid values assert. Test CLI/env precedence, required `run_temp_dir`, env-name overrides, and choices for output/trace formats.
