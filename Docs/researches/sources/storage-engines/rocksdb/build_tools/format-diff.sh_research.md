# sources/storage-engines/rocksdb/build_tools/format-diff.sh research

Purpose: `format-diff.sh` checks or applies clang-format changes only to modified lines, and additionally adds standard copyright headers to newly added `.h`, `.cc`, and `.py` files.

Important APIs: options are `-c` for check-only, `-y` for non-interactive auto-apply, and `-h` for usage. Environment variables include `CLANG_FORMAT_DIFF`, `PYTHON`, `FORMAT_REMOTE`, `FORMAT_UPSTREAM`, `VERBOSE_CHECK`, and normal Git state.

Control flow: it parses options, resolves repo root, locates a working `clang-format-diff` command or script, validates Python support when needed, then enables `set -e`. If there are uncommitted changes, it formats diff hunks against `HEAD`; otherwise it formats changes since the merge base with the RocksDB upstream branch. It detects newly added files and prepends copyright headers when missing. If clang-format produces no diff, it exits cleanly. In check-only mode it exits 1 for needed formatting. Otherwise it prints a colored diff, prompts unless `-y`, applies formatting, and can optionally amend the last commit in post-commit mode.

State and persistence: it can modify source files by adding headers and applying clang-format diffs. It can also run `git commit --amend` after user confirmation. Temporary files are created via `mktemp` for header insertion.

Dependencies and integration: it depends on Git, Bash, clang-format-diff, clang-format, optional Python, sed, curl instructions for missing tools, and repository remote metadata. It is used by developer formatting workflows and possibly `make format`.

Risks and test signals: the script mutates files even before final formatting decisions when adding copyright headers. Some variables and test expressions are unquoted. It only excludes `third-party/`. Interactive `/dev/tty` reads fail in non-interactive contexts unless `-y` or `-c` is used. Tests should cover check-only, auto-apply, uncommitted and post-commit modes, missing tool resolution, and new-file header insertion.
