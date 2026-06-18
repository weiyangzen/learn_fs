# sources/storage-engines/wiredtiger/test/cppsuite/create_test.sh

Purpose: Scaffolds a new cppsuite test source, config file, run dispatch entries, and test-data metadata.

Important APIs/types/functions: validates the test name with `^[a-z][_a-z0-9]+$`, checks target files do not exist, copies `test_template.cpp` and `test_template_default.txt`, rewrites placeholder names with `sed`, inserts includes/dispatch/all-test entries into `tests/run.cpp`, adds metadata to `dist/test_data.py`, and runs `dist/s_all`.

Control flow: fails early for missing/invalid/existing inputs, performs text substitutions, updates multiple registry files, then runs formatting/regeneration.

State and persistence: creates `tests/<name>.cpp` and `configs/<name>_default.txt`; mutates `tests/run.cpp` and `dist/test_data.py`.

Dependencies/integration: depends on template files, GNU-style `sed -i`, and the `s_all` distribution script.

Risks and test signals: textual insertion anchors can break if templates or registry layout change. The script is intentionally mutating and should be run from the cppsuite directory. `s_all` success is the primary generated-code/test-data signal.
