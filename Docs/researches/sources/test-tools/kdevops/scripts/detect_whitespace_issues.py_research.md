<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/detect_whitespace_issues.py -->
# sources/test-tools/kdevops/scripts/detect_whitespace_issues.py

Purpose: detects trailing whitespace, missing final newlines, and more than two consecutive blank lines in text files.

Important APIs and functions: `check_file_whitespace(file_path)` reads bytes, skips null-containing binaries, decodes lines preserving endings, reports per-line trailing whitespace, missing final newline, and excessive blank blocks. `main()` accepts explicit paths or defaults to modified git files, skips common binary suffixes, prints a summary, and returns 1 when issues are found.

Control flow: discover paths, skip missing/binary-like files, aggregate issue counts, print fix guidance, return status.

State and persistence: read-only; no file modifications.

Dependencies and integration: standard library plus git for default mode. `scripts/style.Makefile` invokes it as a style checker.

Risks: decoding with `errors="ignore"` can hide invalid UTF-8 and still scan partially. The default `git diff --name-only` only covers unstaged changes relative to the index, not all tracked files. Emoji output may not be desirable in strict logs. Test signals include fixtures for each whitespace issue, binary skip, missing path warning, and exit status with explicit path lists.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/detect_whitespace_issues.py -->
