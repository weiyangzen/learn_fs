# File Research: sources/local-fs/ocfs2-tools/mkinstalldirs

Portable shell helper for creating installation directory hierarchies.

Key responsibilities:
- Parses `--help`, `--version`, and `-m MODE`.
- Uses `mkdir -p` or `mkdir -m MODE -p` when available.
- Falls back to manually creating each path component.
- Applies mode with `chmod` in fallback mode.
- Handles path components beginning with `-` by prefixing `./`.

Research notes:
- This is the standard Automake-era public-domain `mkinstalldirs` script.
- It reports commands as it runs them.
- It exits with accumulated error status from failed mkdir/chmod operations.
