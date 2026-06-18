# File Research: sources/os/bsd/netbsd-src/sys/sys/disklabel_rdb.h

Defines Amiga Rigid Disk Block partitioning structures and filesystem type identifiers.

Key content:
- `RDBNULL`, `RDB_MAXBLOCKS`.
- `struct rdblock`: RDSK header, checksum fields, linked-list heads for bad/partition/fs blocks, disk geometry, controller/disk inquiry strings.
- RDB flags for last drive/LUN/unit, reselection, disk/controller id, sync.
- `struct ados_environ`: partition filesystem environment table.
- `struct partblock`, `struct badblock`, `struct fsblock`, `struct lsegblock`.
- Block ID constants: `RDSK`, `PART`, `BADB`, `FSHD`, `LSEG`.
- DOS type constants for BSD, NetBSD root/swap/user, AmigaDOS, AMIX, ext2, Linux swap, RAID, MSDOS, SFS.
- `struct adostype`, architecture type constants, and `ISFSARCH_NETBSD`.

Important behavior:
- Represents big legacy on-disk structures with linked blocks.
- Used to translate Amiga partition metadata into NetBSD disklabel semantics.
