# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/appendfiletombox.c

- Role: Appends a message/file stream to a mailbox or file while preserving mbox format rules.
- Key functions: `appendfiletombox` escapes line-start `From ` by inserting a leading space and ensures mailbox entries end with blank lines; `appendfiletofile` appends raw content.
- State: `Inbuf` maintains a 64 KiB buffer, read/write cursors, byte count, and last byte written.
- Integration: Used by mail delivery code.
- Risks/notes: Operates on raw file descriptors and returns `-1` on read/write failure; caller owns locking.
