# sources/user-network-fs/nfs-utils/support/reexport/reexport.h

Purpose: `reexport.h` declares reexport modes and the public helper functions that export parsing/mountd code use.

Important APIs and types: It defines `REEXP_NONE`, `REEXP_AUTO_FSIDNUM`, `REEXP_PREDEFINED_FSIDNUM`, and `REEXP_DB`, plus `reexpdb_init`, `reexpdb_destroy`, `reexpdb_fsidnum_by_path`, `reexpdb_uncover_subvolume`, and `reexpdb_apply_reexport_settings`. `FSID_SOCKET_NAME` sets the default abstract Unix socket.

State, dependencies, and integration: The header includes `exportfs.h` for `struct exportent` and coordinates with `fsidd.service`, `fsidd.c`, and `reexport.c`.

Risks and test signals: Mode values are ABI/config semantics for export options. The abstract socket default starts with `@`, which both client and daemon translate into a NUL-prefixed Unix path. Tests should compile consumers, parse each reexport mode, and verify socket override compatibility.
