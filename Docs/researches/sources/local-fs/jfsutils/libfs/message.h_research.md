# File Research: sources/local-fs/jfsutils/libfs/message.h

This header declares:

- `message_user(unsigned, char **, unsigned, int);`
- Message-file selectors `OSO_MSG` and `JFS_MSG`.
- Symbolic message IDs for common JFS and OSO messages used by mkfs/fsck/extendfs/defragfs paths.

It does not declare the many raw numeric JFS message IDs handled directly in `message.c`; those remain implicit numeric cases.
