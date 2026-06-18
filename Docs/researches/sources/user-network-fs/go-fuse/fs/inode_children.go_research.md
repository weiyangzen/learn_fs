# sources/user-network-fs/go-fuse/fs/inode_children.go

Purpose: deterministic child map for directory inodes.

Important types/functions: `childEntry`; `inodeChildren` stores `childrenMap` name-to-index plus insertion-ordered `children` slice. `set` adds/replaces children, compacts when slice capacity is exhausted, updates parent and child change counters, and records parent links. `del` removes child mapping and parent link. `list` returns entries in deterministic insertion order; `toMap` returns a copy.

Control flow/state: deleted slots remain until compaction; ordering stability supports directory offsets and avoids cache corruption from randomized map iteration.

Dependencies/integration: used by `Inode` tree operations and bridge fallback readdir. Risks include offset stability after mutation, compaction timing, and parent link consistency. Directory and inode tests exercise this indirectly.
