## sources/user-network-fs/samba/source3/lib/smbrun.c

Purpose: shell-command execution helper for Samba code that needs to run configured commands as the active SMB user. It defines the global `struct current_user current_user` used to pick the child UID/GID, creates optional temporary output capture, drops privileges in the child, and invokes `/bin/sh -c`.

Important functions are `smbrun`, `smbrun_no_sanitize`, `smbrunsecret`, and private `smbrun_internal`/`setup_out_fd`. `smbrun` sanitizes shell expansion by passing the command through `escape_shell_string`; `smbrun_no_sanitize` is reserved for known-safe shell uses. `smbrunsecret` sends a secret to the child over stdin through a pipe.

Control flow: output capture creates an unlinked `tmpdir()/smb.XXXXXX` file with group/other permissions masked. `smbrun_internal` preserves the existing SIGCLD handler, forks, waits in the parent with EINTR handling, rewinds the output fd, and returns child exit status. The child installs normal child handling, dup2s the output fd to stdout when requested, calls `become_user_permanently`, verifies real/effective UID/GID unless in non-root mode, closes descriptors from 3 upward, and executes `/bin/sh`. `smbrunsecret` follows similar parent/child logic but dup2s a pipe to stdin and writes the secret from the parent.

State and persistence: no durable state is written. Output temp files are unlinked immediately and survive only via fd. The code depends on global process identity, signal handlers, `/bin/sh`, Samba privilege helpers, `tmpdir`, and `closefrom`.

Risks: all commands still run through a shell, so caller-provided content must be tightly controlled; the unsanitized entry point is explicitly dangerous outside trusted printing/config contexts. `smbrunsecret` does not sanitize `cmd`, writes the secret once without retrying partial writes, and calls `fsync` on a pipe. Test signals are mostly integration-level: correct UID/GID drop, fd hygiene, output capture, shell quoting, and child exit status behavior should be covered by command-execution and printer-command tests.
