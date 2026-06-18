<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/clang-tidy.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/clang-tidy.yml

Purpose: Runs clang-tidy on changed files for push and pull_request events and uploads a comment artifact.

Important APIs/types/functions: job `clang-tidy` uses a RocksDB Ubuntu 24.1 container, checkout depth 2, diff-base calculation, `apt-get install clang-tidy-21`, CMake compile commands generation with clang-21, `tools/run_clang_tidy.py` with GitHub annotations/summary/comment output, and artifact upload.

Control flow: skips new branch pushes with all-zero `github.event.before`; otherwise determines base SHA, builds `compile_commands.json`, runs clang-tidy on changed files with `continue-on-error`, saves PR number for PR events, uploads artifacts, and finally fails the job if clang-tidy found issues.

State and persistence behavior: creates `build/compile_commands.json`, symlink `compile_commands.json`, `clang-tidy-comment.md`, `pr_number.txt`, and the uploaded `clang-tidy-result` artifact.

Dependencies and integration points: paired with `clang-tidy-comment.yml`; depends on CMake, clang-21, `tools/run_clang_tidy.py`, and the container image.

Risks: repository-owner guard prevents fork owners from running this workflow. Push diff base handling can skip or mis-scope unusual histories. CMake config cost is paid even for small diffs.

Test signals: annotations, step summary, uploaded comment artifact, and final failure when issues are found.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/clang-tidy.yml -->
