# sources/storage-engines/rocksdb/tools/run_clang_tidy.py

## Purpose
This Python tool runs `clang-tidy` on changed C/C++ source files and filters diagnostics to lines changed by local commits, staged/unstaged edits, and untracked files. It supports CI annotations, GitHub step summaries, PR comment bodies, parallel execution, explicit diff bases, and optional full-output capture.

## Important APIs, Types, and Functions
Key functions include `run_cmd`, `get_repo_root`, `find_remote_base`, `resolve_diff_base`, `parse_diff_for_changed_lines`, `collect_changed_lines`, `load_compile_db`, `invoke_clang_tidy`, `filter_to_changed_lines`, `emit_github_annotations`, `build_markdown_summary`, `write_github_step_summary`, `write_comment_file`, and `main`. It uses `ThreadPoolExecutor` to run clang-tidy jobs concurrently.

## Control Flow
`main` parses CLI options, discovers the repo root and compile database, resolves the diff base, collects changed line numbers, filters to changed `.cc`/`.cpp` files present in `compile_commands.json`, runs clang-tidy for each file, filters diagnostics to changed lines, optionally writes raw output, emits summaries/annotations/comments, and exits nonzero only when errors are found.

## State and Persistence
The script reads Git state and `compile_commands.json`. It can write a full raw output file, append to `$GITHUB_STEP_SUMMARY`, and write a Markdown comment body containing a stable HTML marker. It does not modify source files.

## Dependencies and Integration Points
It depends on Git, Python 3, clang-tidy, a CMake-style `compile_commands.json`, and GitHub Actions environment conventions when CI flags are used. It integrates with PR workflows by limiting reported findings to changed lines.

## Risks
Diff parsing is custom and may miss rename/delete edge cases or unusual diff headers. Explicit `--diff-base` intentionally ignores working-tree changes. Untracked headers are counted, but only `.cc`/`.cpp` files are linted. The script exits `0` for warnings-only findings, which may or may not match policy. Markdown includes GitHub emoji shortcodes and details blocks, so consumers should support GitHub-flavored Markdown.

## Test Signals
Useful validation includes no-change runs, untracked-file runs, explicit-base CI runs, timeout handling, annotation formatting, and compile database filtering. No dedicated unit tests are present in this subset.
