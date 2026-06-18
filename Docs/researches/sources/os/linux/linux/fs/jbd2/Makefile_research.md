# File Research: sources/os/linux/linux/fs/jbd2/Makefile

Builds the JBD2 journaling object when `CONFIG_JBD2` is enabled.

`jbd2-objs` consists of:
- `transaction.o`
- `commit.o`
- `recovery.o`
- `checkpoint.o`
- `revoke.o`
- `journal.o`
