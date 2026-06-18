# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_scan.c

Purpose: Scans eraseblocks at mount/build time, validates on-flash node headers, creates vnode caches, collects node refs, and classifies eraseblocks into free/clean/dirty states.

Key entry points:
- `chfs_scan_make_vnode_cache`: get or create a vnode cache during scan.
- `chfs_scan_check_node_hdr`: verifies magic and header CRC.
- `chfs_scan_check_vnode`: validates vnode nodes and keeps the highest-version vnode metadata.
- `chfs_scan_check_dirent_node`: validates dirent nodes, name CRC, and parent vnode-cache membership.
- `chfs_scan_check_data_node`: validates data-node metadata CRC and adds an unchecked data-node ref.
- `chfs_scan_classify_cheb`: classifies eraseblock state.
- `chfs_scan_eraseblock`: main eraseblock scanning loop.

Important behavior:
- Free space is detected by repeated `0xff` node-header reads up to `MAX_READ_FREE(chmp)`.
- Bad magic/header CRC causes a 4-byte dirty advance and continued scan.
- Vnode nodes are versioned; older vnode metadata becomes dirty.
- Directory entries are sorted by name hash during scan and version-replaced when duplicate names are found.
- Data nodes are intentionally not data-CRC checked during scan; they become `CHFS_UNCHECKED_NODE_MASK`.
- Padding nodes are marked obsolete and counted dirty.

Dependencies:
- Uses vnode-cache hash from `chfs_vnode_cache.c`.
- Uses node-list and dirty accounting from `chfs_nodeops.c`.
- Uses allocation from `chfs_malloc.c` and flash IO via `chfs_read_leb`.

Research notes:
- Scan updates mount/block accounting aggressively and asserts eraseblock byte totals after each major path.
- The directory-entry scan path maintains a separate `scan_dirents` list before directories are loaded into inodes.
