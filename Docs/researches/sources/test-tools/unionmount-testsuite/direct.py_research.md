# sources/test-tools/unionmount-testsuite/direct.py

Purpose: command-line direct-operation dispatcher for replaying a single open or VFS operation without full suite setup.

Important APIs/types/functions: `parse_C_int`, `direct_open_file`, and `direct_fs_op`.

Control flow: `direct_open_file` parses `--open-file` options into `test_context.open_file` keyword arguments, resolves errno names, creates a direct-mode context, and performs the open. `direct_fs_op` parses `--chmod`, `--link`, `--mkdir`, `--readlink`, `--rename`, `--rmdir`, `--truncate`, `--unlink`, or `--utimes`, maps common flags (`-L`, `-l`, `-B`, `-E`, etc.), creates a direct-mode context, and dispatches to the matching context method.

State and persistence: no setup state is created; operations act directly on caller-supplied paths and can mutate the filesystem.

Dependencies and integration: used by `run` before normal cleanup/setup handling. Depends on `argparse`, `errno`, `ArgumentError`, and `test_context`.

Risks: `parse_C_int` slices octal/decimal strings with `s[2:]`, which misparses common values like `0755` and decimal strings; the `--link` dispatcher calls `ctx.rename` instead of `ctx.link`; direct mode omits layer validation.

Test signals: direct replay commands printed by context methods should exercise these paths.
