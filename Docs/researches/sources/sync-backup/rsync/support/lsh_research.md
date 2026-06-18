<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/lsh -->
# sources/sync-backup/rsync/support/lsh

Purpose: Perl local-shell replacement that emulates a remote shell for localhost-only rsync testing, including optional user switching and optional `rrsync` forced-command emulation.

Important APIs/types/functions: option parsing via `Getopt::Long`; main command construction; `usage()`. Options include ignored ssh-like flags, `-l USER`, `--no-cd`, `--sudo`, `--rrsync=DIR`, and `--rropts=STR`.

Control flow: parse ssh-style options until host/command, accept only `localhost` or `lh`, derive login user from `user@host` or `-l`, optionally switch UID/GID directly or prepend `sudo -H -u`, chdir to the target user's home unless disabled, and either exec `/bin/sh -c <command>` or set `SSH_ORIGINAL_COMMAND` and exec `rrsync` with requested options.

State and persistence behavior: mutates process UID/GID, environment variables (`USER`, `USERNAME`, `HOME`, `SSH_ORIGINAL_COMMAND`), current directory, and then replaces itself with the target command.

Dependencies and integration points: depends on Perl, system passwd/group databases, optional sudo, `/bin/sh`, and optional `rrsync`. It integrates with rsync via `RSYNC_RSH` or `-e`.

Risks: direct UID/GID switching requires privileges and can fail partially; the script checks both real and effective IDs. Command execution through `/bin/sh -c` preserves shell-evaluation risks consistent with remote-shell semantics. Only localhost names are accepted by design.

Test signals: use as `RSYNC_RSH` for local push/pull tests, cover `lh` no-chdir behavior, `localhost` home chdir, `-l` user switching, `--sudo`, and `--rrsync` option forwarding.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/lsh -->
