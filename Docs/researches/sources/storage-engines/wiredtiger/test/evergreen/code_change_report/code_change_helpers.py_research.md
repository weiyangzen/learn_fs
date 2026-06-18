<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_helpers.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_helpers.py

Purpose: shared helper module for diff and Metrix++ complexity processing in the code-change report pipeline. It converts pygit2 diffs to `ChangeInfo` lists and normalizes Metrix++ CSV data.

Important APIs: `is_useful_line(content)` filters blank lines and lone braces so gcov line counts are not treated as meaningful code. `diff_to_change_list(diff)` iterates pygit2 patches, logs status and hunk ranges, wraps each hunk in `ChangeInfo`, and returns `{new_file_path: [hunks...]}`. `read_complexity_data(path)` loads CSV rows as dictionaries. `preprocess_complexity_data(rows)` rewrites leading `./` paths to `src/`, groups by file, and indexes only rows whose `type` is `function` by `region` name.

State and persistence: reads CSV files but writes nothing. Returned dictionaries are consumed by code-change and per-test coverage scripts.

Dependencies and integration: imports `csv`, `logging`, `pygit2.Diff`, and local `ChangeInfo`. The path rewrite is tightly coupled to running Metrix++ from `src/` while gcovr and git diffs use `src/...` paths.

Risks and test signals: duplicate function names in a file overwrite earlier rows. `is_useful_line` is intentionally simple and can still count comments/preprocessor-only lines. Diff parsing correctness depends on pygit2 patch objects and new-file path uniqueness.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_helpers.py -->
