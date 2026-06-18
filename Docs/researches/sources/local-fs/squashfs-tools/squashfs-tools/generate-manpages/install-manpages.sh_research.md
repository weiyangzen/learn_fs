# File Research: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/install-manpages.sh

Installer helper for SquashFS tool manpages.

Arguments:
- Source/git root path.
- Manpage install directory.
- Whether to force prebuilt manpages (`y`/`n`).

Behavior:
- Validates source root by checking for `squashfs-tools/generate-manpages/functions.sh`.
- Sources shared functions.
- Skips cleanly if install path is empty.
- Requires `gzip`.
- Uses prebuilt manpages when requested, when GNU sed is unavailable, when `help2man` is unavailable, or when custom generation fails.
- Attempts to generate custom manpages for `mksquashfs`, `unsquashfs`, `sqfstar`, and `sqfscat`.
- Installs and gzip-compresses each `.1` page with `gzip -n -f9`.

Notable risks/quirks:
- Many variables and paths are unquoted.
- Fallback warning text contains nested unescaped `"y"` inside a double-quoted string, which is shell-fragile as written.
