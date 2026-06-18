# File Research: sources/local-fs/xfsdump/librmt/rmtcommand.c

Implements `_rmt_command(fildes, buf)`.

Behavior:
- Writes a complete text command to the remote process pipe.
- On short/failing write, aborts the remote unit and sets `errno = EIO`.
- Emits debug logging.

Role:
- Shared command-send primitive for all remote operations.
