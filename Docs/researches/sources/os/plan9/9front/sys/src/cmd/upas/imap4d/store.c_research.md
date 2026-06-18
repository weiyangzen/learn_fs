# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/store.c

Implements IMAP flag store/update behavior.

Key responsibilities:
- Maps IMAP system flags to internal bitmasks.
- Applies `STORE FLAGS`, `+FLAGS`, `-FLAGS`, and `.SILENT` variants.
- Prevents clients from modifying `\Recent`.
- Marks dirty `.imp` state and queues unsolicited flag updates when needed.
- Emits `FETCH FLAGS` updates.

Important functions:
- `storemsg()` applies a parsed `Store` operation to a message.
- `setflags()` updates message flags and mailbox recent count.
- `sendflags()` emits pending flag updates.
- `writeflags()` serializes flags.
- `msgseen()` marks messages seen when fetched.
- `mapflag()` maps parser flag names to bits.

Filesystem relevance:
- Any flag change marks `.imp` dirty; `closeimp()` later persists it.
- Does not directly mutate upas/fs message files except through `.imp`.
