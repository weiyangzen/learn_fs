# File Research: sources/local-fs/jfsutils/mkfs/inodemap.c

Initializes the first inode allocation map extent for either aggregate or fileset inode maps.

Important functions:
- `init_AG_free_list(...)`: determines which allocation group contains the initial inode extent and initializes that AG’s free-inode/free-extent list entries. Other AG entries are set empty.
- `init_inode_map(...)`: allocates a combined inode-map buffer, initializes the dinomap control page and first IAG, writes it to disk, and marks the inode-map blocks allocated in the block map.

Key metadata initialized:
- `dinomap` fields: free IAG, next IAG, inode counts, free counts, blocks per inode extent.
- First `iag`: IAG number, AG start, free-list pointers, free inode/extent counts, working and persistent maps.
- First inode extent descriptor points at the initialized inode table.
- Summary maps (`extsmap`, `inosmap`) are derived from extent descriptors and inode bitmaps.

Special case:
- Aggregate inode map uses initial bitmap `0xf8008000`.
- Fileset inode map uses `0xf0000000`.

Filesystem relevance: creates the on-disk inode allocation structures required before a fresh JFS filesystem can allocate inodes.
