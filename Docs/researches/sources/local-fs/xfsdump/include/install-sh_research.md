# File Research: sources/local-fs/xfsdump/include/install-sh

`install-sh` is a bash install helper emulating BSD install with xfsdump packaging extensions.

Supported modes:
- Create a directory with `-d`.
- Install one file to a target file or directory.
- Install multiple files to a directory.
- Create a symlink with `-S`.
- Install libtool-built libraries with `-T` submodes such as `so_dot_version`, `so_dot_current`, `so_base`, and `old_lib`.

Environment behavior:
- `DIST_ROOT` or `DESTDIR` prefixes installation targets.
- `DIST_MANIFEST` records manifest entries.
- If `DIST_MANIFEST` is set without `DIST_ROOT`, the script records manifest entries but suppresses actual copy/link/mkdir/chmod/chown actions.
- Manifest records use `f`, `d`, or `l` lines for files, directories, and symlinks.

Ownership behavior:
- `_chown` tries `chown owner:group target`.
- Non-root failures can be suppressed with a one-time warning marker at `$DIST_ROOT/.chown.quiet`.
- When installing into `DIST_ROOT` as non-root, `CHOWN=true` disables ownership changes.

Maintenance/security notes:
- The script uses many unquoted variable expansions (`$dir`, `$f`, `$target`, etc.), so paths with spaces or shell metacharacters are fragile.
- It sources `./$libtool_lai` for `-T`, which is expected in build tooling but should not be pointed at untrusted files.
