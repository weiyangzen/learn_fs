# File Research: sources/local-fs/ocfs2-tools/fswreck/journal.c

This file corrupts OCFS2 journal system files.

Key behavior:
- `mess_up_journal()` resolves the journal system inode for the requested slot, reads its cached inode, maps the first journal block, and reads the JBD2 journal superblock.
- `JOURNAL_FILE_INVALID` flips the JBD2 magic.
- `JOURNAL_UNKNOWN_FEATURE` sets unknown incompatible and read-only compatible feature bits.
- `JOURNAL_MISSING_FEATURE` requires multiple slots, sets all known features on an adjacent journal, then clears known features on the target journal.
- `JOURNAL_TOO_SMALL` sets the journal inode’s cluster count to zero.
- Writes the modified journal superblock and cached inode.

Integration notes:
- Depends on libocfs2 cached inode and extent map APIs plus JBD2 constants.
- Slot default is the last configured slot when caller passes `UINT16_MAX`.
