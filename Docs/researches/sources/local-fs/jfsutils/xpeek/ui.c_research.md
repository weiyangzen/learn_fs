# File Research: sources/local-fs/jfsutils/xpeek/ui.c

Provides shared UI parsing for interactive metadata modification commands.

Main API:
- `m_parse(char *cmd_line, int n_fields, char **value)`.

Behavior:
- Assumes the caller has already parsed the `m` subcommand with `strtok`.
- Reads a field number from the remaining command line or prompts interactively.
- Validates field number is in `1..n_fields`.
- Extracts exactly one value token.
- Rejects missing or extra arguments.
- Returns the selected field number, or `0` on parse/validation failure.

Integration points:
- Used by most editor commands: inode, iag, dmap, dtree/xtree, fsck workspace, logsuper, and superblock handlers.

Notable behavior and risks:
- Only supports single-token values; labels, strings, or names containing spaces cannot be entered through this parser.
- Uses fixed prompt read length of 80 bytes supplied by callers.
- Does not perform numeric conversion itself, so each caller must validate conversion semantics.
