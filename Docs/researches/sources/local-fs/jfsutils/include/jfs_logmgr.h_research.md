# File Research: sources/local-fs/jfsutils/include/jfs_logmgr.h

Defines JFS journal/log manager disk structures and log record descriptors.

Key contents:
- Log page size constants and log superblock block numbers.
- Defines log magic/version and max active filesystems sharing a log.
- `struct logsuper` stores magic, version, serial, size, block size, flags, state, end pointer, uuid/label, and active filesystem UUIDs.
- Defines log states: mounted, redone, wrapped, read error.
- `struct logpage` defines header/data/trailer page layout with page sequence and end-of-record markers, including split-write detection commentary.
- Defines log record type flags: commit, sync point, mount, redopage, noredopage, noredoinoext, updatemap, noredofile.
- Defines record subtype flags for inode, xtree, dtree, btroot, EA, ACL, data, new, extend, relocate, directory xtree, and allocation/free extent variants.
- `struct lrd` is the fixed log record descriptor with transaction id, backchain, type, length, aggregate, and type-specific union payloads.

Interactions:
- Used by logredo/logdump/log formatting code in `libfs`.
- Depends on `jfs_types.h` and `jfs_filsys.h`.

Research notes:
- Comments document recovery ordering and split-write handling assumptions; this is core journal replay format documentation.
