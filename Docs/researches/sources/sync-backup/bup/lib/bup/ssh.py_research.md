## sources/sync-backup/bup/lib/bup/ssh.py

Purpose: starts a remote `bup` subcommand over SSH, or a local subprocess in test mode.

Important APIs and control flow: `connect(destination, port, subcmd, stderr=None)` validates `subcmd` with a strict alphanumeric/dash/underscore regex. Empty destination or `b'-'` is accepted only when `BUP_TEST_LEVEL` is set, in which case it runs `[path.exe(), subcmd]`. Real remote mode builds `ssh [-p port] destination -- sh -c 'BUP_DEBUG=... BUP_FORCE_TTY=... bup subcmd'` and returns a `Popen` with piped stdin/stdout and a new session.

State and dependencies: environment values come from `bup.compat.environ`; executable path comes from `bup.path.exe()`. It integrates with remote repository operations through client-side transports.

Risks and tests: destination and port are passed as argv elements, but the remote shell command interpolates debug values and `subcmd`; the regex is the key injection control for `subcmd`. Test mode is guarded to avoid accidental local execution. Remote behavior is indirectly covered by `bup on`, `save -r -:repo`, `init --remote`, and `test-gc` remote scenarios.
