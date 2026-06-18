# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/dat.h

Central private data header for fossil storage code.

It defines core constants, disk header/superblock values, block states, block types, I/O states, disk partition ids, and the main structs: `Fs`, `Super`, `Entry`, `Source`, `Header`, `Label`, `Block`, `WalkPtr`, and `Fsck`. It also documents important epoch locking rules: ordinary file operations take a read lock on `Fs.elk`, while snapshot creation/removal takes the write lock.

The structures encode fossil's local/Venti hybrid model: `Entry` extends Venti entries with local tag/snapshot/archive fields, `Source` maps file streams to entry slots, and `Block` carries cache-private dependency, dirty, label, and I/O metadata.
