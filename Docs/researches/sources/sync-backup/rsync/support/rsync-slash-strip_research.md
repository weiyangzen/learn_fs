<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/rsync-slash-strip -->
# sources/sync-backup/rsync/support/rsync-slash-strip

Purpose: bash wrapper that strips one trailing slash from each non-root rsync command-line argument before invoking real rsync, changing `src/` semantics to match `src`.

Important APIs/types/functions: constant `REAL_RSYNC=/usr/bin/rsync`; main loop builds `args=()`.

Control flow: iterate original arguments, bypass immediately to real rsync if `--server` is present, preserve `/` exactly, otherwise append `${arg%/}` to remove one trailing slash, then exec real rsync with transformed arguments.

State and persistence behavior: no persistent state. It only transforms argv.

Dependencies and integration points: depends on bash arrays and rsync. It is intended as a user command alias/wrapper, not a server-side filter.

Risks: it strips trailing slashes from every argument, including option values and remote specs, which may be surprising. Users must use `src/.` or `src//` when they really want directory contents. Server mode must bypass to avoid corrupting rsync protocol invocation.

Test signals: verify `src/` becomes `src`, `/` remains `/`, `src//` becomes `src/`, and server-mode arguments are untouched.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/rsync-slash-strip -->
