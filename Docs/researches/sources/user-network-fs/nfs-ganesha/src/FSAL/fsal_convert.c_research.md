## sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_convert.c

### Purpose
`fsal_convert.c` translates between POSIX/kernel filesystem concepts and nfs-ganesha FSAL abstractions: errno to `fsal_errors_t`, mode/test/open flags, object types, device IDs, and `stat` attributes.

### Important APIs, Types, And Functions
`posix2fsal_error` maps POSIX errors into FSAL major codes, logging notable IO, NXIO, memory, delay, and default server-fault cases. `fsal2posix_testperm` converts `FSAL_R_OK`, `FSAL_W_OK`, and `FSAL_X_OK` to `R_OK`, `W_OK`, and `X_OK`. `posix2fsal_type` maps `S_IF*` mode bits to `object_file_type_t`. `posix2fsal_fsid` and `posix2fsal_devt` split `dev_t` into major/minor structures. `fsal2posix_openflags` maps read/write/truncate FSAL open flags to POSIX `O_*` flags. `object_file_type_to_str` is a diagnostic helper. `posix2fsal_attributes_all` and `posix2fsal_attributes` fill `struct fsal_attrlist` from `struct stat`.

### Control Flow
Error conversion is a large switch with platform-specific cases for Linux and AIX. Attribute conversion checks `fsalattr->valid_mask` before writing each field, obtains the supported mask from `op_ctx->fsal_export->exp_ops.fs_supported_attrs`, computes `change` as the newer of mtime and ctime in nanoseconds, converts `st_blocks` to `spaceused`, and maps raw device numbers for special files.

### State And Persistence
The file has no persistent state. It reads global request context through `op_ctx` in `posix2fsal_attributes`, so conversion depends on a current FSAL export context. Outputs are caller-owned structs.

### Dependencies And Integration Points
It depends on POSIX headers, `fsal.h`, `fsal_convert.h`, and `common_utils.h`. VFS-like FSALs and local filesystem code use these helpers when translating syscalls into FSAL responses. `localfs.c` uses device conversion for filesystem indexing. `fsal_up_async.c` uses `posix2fsal_error` to convert `fridgethr_submit` failures.

### Risks
`posix2fsal_error` maps `EBADF` to `ERR_FSAL_NOT_OPENED`, with a comment noting this can be wrong for write-on-read-only-FD cases. Unknown errno values become `ERR_FSAL_SERVERFAULT`, so new platform errors can surface as severe faults. `fsal2posix_openflags` intentionally ignores some FSAL flags; callers must handle create/exclusive/share semantics elsewhere. Attribute conversion requires valid `op_ctx`; calling it outside an operation context can dereference invalid state.

### Test Signals
Tests should cover errno mappings including retry and unsupported cases, file type conversion for every `S_IF*`, open flag combinations, major/minor conversion, valid-mask driven attribute population, and `ATTR_CHANGE` selection between mtime and ctime.
