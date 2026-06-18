# File Research: sources/os/bsd/dragonflybsd/sys/sys/journal.h

Defines the on-disk/on-wire binary record format for DragonFly’s VFS journaling stream. The file documents raw record alignment, forward/backward scanning, stream IDs, endian detection, transaction begin/end/abort bits, and nested subrecord semantics.

Key types are `journal_rawrecbeg`, `journal_rawrecend`, `journal_ackrecord`, `journal_subrecord`, and low-level leaf structures such as `jleaf_path`, `jleaf_vattr`, `jleaf_cred`, and `jleaf_ioinfo`. Constants define stream control bits, special stream IDs, max record sizes, nested record masks, VFS operation record types (`JTYPE_CREATE`, `JTYPE_RENAME`, `JTYPE_WRITE`, etc.), and leaf payload IDs. This is the protocol contract used by mount journaling and recovery/audit tools.
