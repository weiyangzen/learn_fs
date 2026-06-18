# sources/test-tools/pynfs/nfs4.1/server_exports.py

Purpose: helper for mounting in-process pynfs test server exports, including memory, disk, block-layout, and file-layout exports.

Important APIs/types/functions: `mount_stuff`, `_create_simple_block_dev`, and `_load_dataservers`.

Control flow: `mount_stuff` creates a disk-backed stub filesystem at `/tmp/py41/fs1`, memory stub filesystems, mounts them at `/a`, `/b`, and `/foo/bar/c`, and conditionally mounts block or file layout exports depending on options. `_create_simple_block_dev` builds a simple/sliced/concatenated block volume over `/dev/ram4`. `_load_dataservers` instantiates `DSDevice`, loads configuration from a file, and returns it.

State and persistence behavior: disk export state persists under `/tmp/py41/fs1` unless reset; memory exports are transient. Block layout state depends on the backing ram device. File-layout state depends on configured data servers.

Dependencies/integration: imports `StubFS_Mem`, `StubFS_Disk`, `BlockLayoutFS`, `FileLayoutFS`, `DSDevice`, and block volume classes. It is used by the local test server setup rather than by client-side tests directly.

Risks and test signals: paths and `/dev/ram4` are hard-coded, making this environment-specific. `_load_dataservers` ends with a semicolon but works in Python. If data-server loading returns `None`, file-layout mount is skipped.
