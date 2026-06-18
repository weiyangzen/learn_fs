# sources/user-network-fs/blobfuse2/component/libfuse/libfuse_defs.h

Purpose: shared C definitions for the cgo libfuse wrapper. It normalizes fuse2/fuse3 type names, defines the C `fuse_options_t` config struct, declares Go-exported callback functions, and lists wrapper/native helper prototypes.

Important APIs/types/functions: typedef aliases for `fuse_operations_t`, `fuse_conn_info_t`, `fuse_config_t`, `fuse_args_t`, `fuse_file_info_t`, `statvfs_t`, `stat_t`, `timespec_t`, and readdir/fill flag enums. Fuse2 placeholder enums provide fuse3-only readdir/fill flags. `fuse_options_t` holds mount path, uid/gid, permissions, timeouts, read-only, allow flags, trace, non-empty, and umask. Extern declarations cover shared callbacks plus version-specific signatures for init/getattr/readdir/truncate/rename/chmod/chown/utimens. Native helper prototypes include `blobfuse_cache_update`, `native_read_file`, `native_write_file`, and `native_flush_file`.

Control flow: the header has no runtime control flow, but preprocessor branches select fuse2 vs fuse3 signatures and constants. The comments document cgo constraints: static C definitions to avoid duplicate symbols, `//export` requirements, no blank line before `import "C"`, and matching C/Go types.

State and persistence behavior: defines `static int fill_dir_plus`, zero for fuse2 and `FUSE_FILL_DIR_PLUS` for fuse3. Other content is type/prototype declarations only. No persistence occurs.

Dependencies/integration points: included by `libfuse_wrapper.h` and cgo handler files. Must match Go exported function names exactly and match libfuse ABI differences between fuse2 and fuse3. It also documents unsupported FUSE operations that Blobfuse does not implement.

Risks: signature mismatches between this header, wrapper code, and Go exports will fail compilation or cause runtime ABI corruption. Static definitions are necessary because cgo may include the header in multiple translation units. The fuse2 placeholder enums must not conflict with real fuse2 headers. Unsupported callback list shows feature gaps such as xattrs, lock, fallocate, copy_file_range, lseek, and ioctl.

Test signals: compile-time cgo builds are the primary test. Runtime callback tests indirectly validate that selected declarations match Go functions for the active fuse version.
