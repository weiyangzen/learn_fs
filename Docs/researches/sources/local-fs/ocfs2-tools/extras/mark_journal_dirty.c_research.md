# File Research: sources/local-fs/ocfs2-tools/extras/mark_journal_dirty.c

Read coverage: complete file read, 263 lines.

Purpose: destructive test/maintenance helper that assigns a node to a slot and marks that slot journal dirty.

Behavior:
- Usage: `mark_journal_dirty <device> <node #> <slot #>`.
- Opens the filesystem read-write.
- Reads the slot map system file, rejects duplicate node entries, writes the supplied node number into the requested slot, and writes the backing slot-map data block directly.
- Looks up the requested slot journal inode.
- Sets `OCFS2_JOURNAL_DIRTY_FL` in the journal inode and writes it back.

Dependencies: `ocfs2_lookup_system_inode()`, `ocfs2_read_whole_file()`, raw slot-map layout, inode read/write helpers, byteorder conversion.

Risk notes:
- This is write-capable and can intentionally make a filesystem require journal recovery.
- Slot bounds are not explicitly checked against `s_max_slots` before `slots[slot]` assignment.
- Main exits `0` even when several operations fail after logging errors.
