# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/nodes.c

Implements small parser-node constructors and message-set iteration helpers.

Key responsibilities:
- Tests sequence/UID membership with `inmsgset()`.
- Iterates message sets by UID or sequence using `formsgs()`, preserving mailbox order and avoiding duplicate operations from overlapping ranges.
- Builds `Store`, `Fetch`, and `Slist` nodes in the `parsebin` arena.
- Reverses fetch/string lists into protocol order.
- Prints numeric and string lists to `Biobuf`.

Important functions:
- `formsgsu()` iterates selected messages and matches UID ranges.
- `formsgsi()` iterates sequence ranges and reports missing sequence numbers as errors.
- `mkstore()`, `mkfetch()`, `mkslist()` allocate parser nodes.
- `revfetch()`, `revslist()` reverse linked lists.

Filesystem relevance:
- Supports IMAP operations over mailbox message lists from `Box`.
- Non-UID operations treat missing expunged sequence references as errors, while UID operations ignore missing messages per IMAP behavior.

Notable quirks:
- Comment notes short-circuiting UID iteration provides little value because expected mailbox sizes are only tens of thousands.
