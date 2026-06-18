# File Research: sources/os/linux/linux-stable/fs/jbd2/Makefile

Builds the JBD2 journaling object.

Composition:
- `obj-$(CONFIG_JBD2) += jbd2.o`
- `jbd2-objs := transaction.o commit.o recovery.o checkpoint.o revoke.o journal.o`

This group covers `commit.o` and `checkpoint.o`; other objects provide transaction, recovery, revoke, and journal infrastructure.
