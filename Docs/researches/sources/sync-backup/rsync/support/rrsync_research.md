<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/rrsync -->
# sources/sync-backup/rsync/support/rrsync

Purpose: restricted rsync forced-command wrapper for ssh authorized_keys deployments, limiting rsync server operations to a configured directory and optional read/write/delete policy.

Important APIs/types/functions: constants `RSYNC`, `LOGFILE`, option policy tables `short_disabled`, `short_disabled_subdir`, `short_no_arg`, `short_with_num`, and `long_opts`; functions `main()`, `validated_arg()`, `lock_or_die()`, `die()`, and `OurArgParser.error()`.

Control flow: parse wrapper options and resolve the restricted dir, optionally lock the directory, read `SSH_ORIGINAL_COMMAND`, require `rsync --server`, determine sender/push mode, apply read-only/write-only/no-delete/no-overwrite policy by disabling rsync options or appending server options, parse the server command using a restricted regex, validate every option and option argument, expand braces/globs for transfer args, reject `..` under non-root restricted dirs, ensure real paths stay under the restricted dir, log the final command if `rrsync.log` exists, and exec or run `/usr/bin/rsync --server ... -- . <args>`.

State and persistence behavior: changes current directory to the restricted dir, optionally holds an advisory flock on that directory, appends to `rrsync.log`, and then either `execlp()`s rsync or waits for a child process. It can add `--munge-links` and `--ignore-existing` to server options.

Dependencies and integration points: depends on Python 3, optional `braceexpand`, glob, socket reverse lookup, fcntl locking, sshd-provided `SSH_ORIGINAL_COMMAND` and `SSH_CONNECTION`, and rsync server option conventions.

Risks: this is security-sensitive argument parsing. Any newly added rsync server option must be reflected in `long_opts`/short tables with the right validation type. It assumes the rsync protocol/command line has not been maliciously hijacked after validation. `realpath()` validation can be affected by races between validation and rsync execution, though the wrapper narrows intended paths significantly. Logging does reverse DNS opportunistically and can block or return unexpected tuple formatting.

Test signals: tests should cover read-only and write-only enforcement, delete-option disabling, subdir disabling of symlink-sensitive short options, absolute path allowance, unsafe symlink/path rejection, brace expansion, glob behavior, files-from/log-file option-argument validation, lock contention, `ssh host true`, and passthrough of valid server commands.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/rrsync -->
