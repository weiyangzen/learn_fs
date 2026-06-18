# File Research: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/functions.sh

Shared shell helpers for manpage generation scripts.

Provides:
- `print()` and `error()` wrappers using an external `echo` binary.
- `check_sed()` to verify a sed executable supports GNU-compatible `-i` behavior and `\U` replacement uppercasing.
- `set_sed()` to use a supplied `SED`, otherwise discover `sed` or `gsed`.

Startup behavior:
- Requires non-builtin `echo` to exist in `PATH`.
- Stores `ECHO=$(which echo)` for later use.

Key role: centralizes GNU sed detection because generated manpage scripts rely on GNU sed extensions.

Notable risks/quirks:
- Uses unquoted shell variables in several command invocations, so paths with whitespace are fragile.
