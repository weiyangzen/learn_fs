# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/problem.h

Read coverage: complete file read, 61 lines.

Purpose: defines the fsck prompt framework and prompt-code integration.

Behavior:
- Defines prompt default flags `PY` and `PN`.
- Wraps `prompt_input()` in a `prompt()` macro that creates a unique symbol containing the prompt code and source line.
- Includes generated `prompt-codes.h`, built from `fsck.ocfs2.checks.8.in`.
- Declares `prompt_input()` with printf-format checking.

Risk notes:
- The unique-symbol trick supports the Makefile duplicate-prompt-code check.
- Prompt documentation and code generation must stay synchronized.
