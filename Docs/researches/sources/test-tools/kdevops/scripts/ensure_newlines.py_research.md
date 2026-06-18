<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/ensure_newlines.py -->
# sources/test-tools/kdevops/scripts/ensure_newlines.py

Purpose: recursively ensures selected text-like files under the current directory end with a newline.

Important APIs and functions: `needs_newline(file_path)` reads bytes, ignores empty and null-containing files, and checks final byte; `add_newline(file_path)` opens append mode and writes `\n`; `main()` walks `.`, skips hidden directories plus `__pycache__` and `node_modules`, and processes known extensions and special filenames.

Control flow: directory walk, file type filter, need check, append newline, count and report.

State and persistence: modifies files in place by appending a newline. It does not preserve binary mode line-ending style if a text file uses CRLF and lacks a final newline.

Dependencies and integration: standard library only. `scripts/style.Makefile` invokes it during style checks, currently with `|| true`, so failures do not stop the style target.

Risks: broad recursive walk can touch many files outside intended changed-file scope. It does not skip all generated/build/cache directories. Bare `except` blocks suppress useful errors. Test signals include temp directory fixtures for targeted suffixes, hidden directory skips, binary skips, CRLF edge cases, and permission-denied behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/ensure_newlines.py -->
