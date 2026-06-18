# File Research: sources/local-fs/xfsdump/librmt/rmtstatus.c

Implements `_rmt_status(fildes)`.

Protocol:
- Reads one newline-terminated status line from the remote process.
- `A<number>` means success and returns the numeric value.
- `E<errno>` means recoverable error; sets `errno` and drains one error-message line.
- `F<errno>` means fatal error; sets `errno`, drains one line, aborts the connection.
- Any unexpected status aborts and sets `EIO`.

Role:
- Central parser for `/etc/rmt` status replies.
