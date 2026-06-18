## sources/user-network-fs/blobfuse2/component/libfuse/libfuse_wrapper.h

Purpose: C shim that adapts blobfuse2's Go-exported libfuse handlers to the `fuse_operations` table for either FUSE2 or FUSE3. It centralizes callback registration and small native helpers required by the Go cgo layer.

Important APIs and flow: `populate_callbacks` assigns destroy, statfs, directory, file, link, sync, attribute, and rename callbacks. Read, write, and flush are wired to `native_read_file`, `native_write_file`, and `native_flush_file` for fast FD-based I/O; commented alternatives show the pure Go handlers. FUSE2 and FUSE3 signatures are selected with `__FUSE2__`. `start_fuse` calls `fuse_main`, `populate_statfs` uses host `/` stats, `populate_uid_gid` lazily captures FUSE context uid/gid, `get_root_properties` synthesizes root stat data, and `fill_dir_entry` adapts `fuse_fill_dir_t` flags.

State and dependencies: Depends on libfuse headers, Linux/POSIX headers, `libfuse_defs.h`, and `native_file_io.h`. It keeps process-global `fuse_opts` and `context_populated`.

Risks: Function pointer casts suppress type checking, so ABI drift between FUSE versions can break at runtime. Root attributes are static and time-based. `populate_uid_gid` is global and not reset across mounts/tests. Test signal comes indirectly from libfuse cgo tests and native I/O behavior.
