# sources/sync-backup/rsync/rsync-web/rsync-debug

Purpose: Debug wrapper that runs rsync under `strace` with core dumps enabled.

Important APIs, types, and functions: Runs `ulimit -c unlimited`, then invokes `strace -f -t -s 1024 -o /tmp/rsync-$$.out rsync "$@"`.

Control flow: Linear wrapper with no option parsing. All user arguments are forwarded to rsync.

State and persistence behavior: Writes an strace log to `/tmp/rsync-<pid>.out` and may allow core files depending on system configuration.

Dependencies and integration points: Depends on shell, `strace`, and rsync. Comments note some systems use `truss` or `tusc`, but the script hard-codes `strace`.

Risks and test signals: Risks include leaking sensitive paths/args/data into `/tmp`, overwriting predictable-ish files if pid reuse and permissions align, and absence of `strace` on non-Linux systems. Test by invoking with harmless rsync args and verifying trace output.
