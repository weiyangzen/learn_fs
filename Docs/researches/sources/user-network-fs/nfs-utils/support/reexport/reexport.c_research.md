# sources/user-network-fs/nfs-utils/support/reexport/reexport.c

Purpose: `reexport.c` is the client-side helper used while parsing exports to obtain stable fsid numbers from `fsidd` and apply reexport policy to `struct exportent`.

Important APIs and control flow: `reexpdb_init` retries the `fsidd` connection, `do_fsidd_cmd` writes one socket request and parses one reply, and wrappers implement path-to-fsid, fsid-to-path, and reconnect behavior. `reexpdb_uncover_subvolume` uses fsid lookup followed by `nfsd_path_statfs` to trigger automounts. `reexpdb_apply_reexport_settings` skips non-reexports, UUID fsids, and v4 roots, then enforces or allocates numeric fsids depending on `e_reexport`.

State, dependencies, and integration: Static `fsidd_srv` caches the socket. It depends on `nfs.conf`, `nfsd_path`, export flags, and the fsidd text protocol.

Risks and test signals: Failed `connect` leaks the just-created socket, replies are capped at 1023 bytes, command strings cannot encode paths containing protocol separators safely, and reconnection closes on parse failures. Tests should cover daemon absence/restart, auto fsid allocation, configured fsid mismatch, v4 root skip, UUID skip, and very long paths.
