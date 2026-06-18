# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/portdat.h

Purpose: Central cwfs data layout and global type definition header. It defines both on-disk structures and in-memory server structures.

On-disk structures:
- `Tag`: block tag footer with tag type and qid path.
- `Qid9p1`: old qid format.
- `Super1`/`Superb`: superblock/free-list metadata.
- `Centry`, `Cache`, `Bucket`: cached-WORM map/cache structures.
- `Dentry`: directory entry layout, including name, uid/gid/mode, qid, size, direct blocks, indirect blocks, and times.
- `Label`: `Devlworm` label stored in the last block with `Labmagic`, side ordinal, and service string.

In-memory structures:
- `Device`: polymorphic device tree node with unions for wren/worm, composite devices, cw, juke, read-only, fake worm, partitions, and byte-swapped devices.
- `Chan`, `Msgbuf`, `Queue`: connection and message queue machinery.
- `File`, `Wpath`, `Tlock`: fid/path/lock bookkeeping.
- `Filsys`, `Conf`, `Cons`, `Uid`, `Iobuf`, `Hiob`, `Rabuf`, `Truncstate`: filesystem, configuration, users, buffer cache, readahead, and truncation state.

Constants:
- `SUPER_ADDR` and `ROOT_ADDR` set fixed super/root block addresses.
- Derived block constants include `BUFSIZE`, `DIRPERBUF`, `INDPERBUF`, `FEPERBUF`, and cache bucket sizing.
- Device types include `Devwren`, `Devworm`, `Devlworm`, `Devfworm`, `Devjuke`, `Devcw`, `Devro`, `Devmcat`, `Devmlev`, `Devpart`, `Devswab`, and `Devmirr`.
- Block tags include super, directory, file, free, bucket, cache, config, labeled-WORM label, and variable-depth indirect tags.

Notable details:
- Packed sections are marked “DONT TOUCH”; changing them changes disk format.
- Under non-`COMPAT32`, deeper indirect block tags up to `Tind4` are supported.
- Global `conf` and `cons` are defined here, so this header contributes storage, not just declarations.
