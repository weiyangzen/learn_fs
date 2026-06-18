<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/evg_cfg.py -->
# sources/storage-engines/wiredtiger/test/evergreen/evg_cfg.py

Purpose: CLI helper to check or generate Evergreen task snippets for test directories that should be represented in `test/evergreen.yml`.

Important APIs: `run()` executes shell commands and returns output. `get_make_check_dirs()` finds `CMakeLists.txt` files with `add_test`, `define_c_test`, or `define_test_variants`, excluding build folders and known subtrees. `get_csuite_dirs()` lists csuite child directories. `find_tests_missing_evg_cfg()` derives make-check task names from directory names and checks whether they appear in the config file. `generate_evg_cfg_for_missing_tests()` fills a template and inserts it before a search marker.

Control flow: argparse supports `check` and `generate`, `-t TEST_TYPE`, and verbose. `evg_cfg()` changes to repo root, runs checks for one or all test types, exits nonzero when missing tasks are found, or edits `test/evergreen.yml` in generate mode.

State and persistence: check mode reads files only; generate mode writes `test/evergreen.yml`.

Dependencies and integration: relies on Git repo root, CMake test declarations, task templates, and marker comments.

Risks and test signals: csuite missing check currently skips every csuite directory, so csuite generation is ineffective. Task existence is substring-based. `generate all` calls generation per type and exits if one type has no missing tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/evg_cfg.py -->
