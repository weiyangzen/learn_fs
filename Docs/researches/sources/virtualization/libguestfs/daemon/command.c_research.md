# File Research: sources/virtualization/libguestfs/daemon/command.c

Core daemon helper for executing external commands and capturing output.

Key points:
- Provides variadic and argv-based wrappers: `commandf`, `commandrf`, `commandvf`, `commandrvf`.
- Uses `fork`, `execvp`, pipes, and `select` rather than shell expansion for normal command execution.
- Can capture stdout and/or stderr into null-terminated buffers; trims trailing newlines from stderr.
- `COMMAND_FLAG_FOLD_STDOUT_ON_STDERR` supports tools that report errors on stdout.
- `COMMAND_FLAG_CHROOT_COPY_FILE_TO_STDIN` lets a chrooted fd be fed to command stdin, used for guest file checksums/hexdumps.
- `COMMAND_FLAG_DO_CHROOT` chroots the child into `sysroot` before execution.
- Resets SIGALRM/SIGPIPE in the child, sets stdin to `/dev/null` unless forwarding a file descriptor, and always waits for child status.
