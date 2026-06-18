# File Research: sources/os/plan9/9front/sys/src/cmd/git/conf.c

Git config query command.

Key responsibilities:
- Locates repository root or prints it with `-r`.
- Reads config values from explicit `-f` files or default repo/user/system config files.
- Supports section-qualified keys using `section.key`.
- Optionally prints all matches with `-a`.

Important behavior:
- Section headers are matched as literal bracketed strings like `[remote "origin"]`.
- Key matching strips whitespace around key/value and `=`.
- Default config search order is `.git/config`, `$home/lib/git/config`, then `/sys/lib/git/config`.

Notable risks:
- Section detection compares against the unstripped line for headers, while other comparisons use stripped text.
