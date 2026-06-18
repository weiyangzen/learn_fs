# File Research: sources/os/linux/linux-stable/fs/9p/v9fs.c
- Purpose: Implements 9P module/session lifecycle, mount option parsing, sysfs cache reporting, and inode-cache setup.
- Main functions: `v9fs_parse_param`, `v9fs_apply_options`, `v9fs_session_init`, `v9fs_session_close`, `v9fs_session_cancel`, `v9fs_session_begin_cancel`, `init_v9fs`, `exit_v9fs`.
- Mount parsing: Uses `fs_context` parameter specs to parse access mode, cache mode, protocol version, debug, uid/gid, dfltuid/dfltgid, aname, cache tag, transport options, and client options.
- Session setup: Allocates/initializes `v9fs_session_info`, creates a 9P client, attaches the root fid, sets cache policy, initializes rename serialization, and registers session state.
- Cache modes: Converts textual cache options into bit flags such as metadata, loose, mmap, fscache, and writeback-related behavior.
- Integration: Provides module init/exit, sysfs session cache visibility, and exports session helpers consumed by superblock setup.
- Risks: Option combinations affect data coherency and writeback semantics; protocol version selection controls whether dotl or legacy operation tables are used.
