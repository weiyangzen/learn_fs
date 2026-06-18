# sources/user-network-fs/samba/source3/modules/vfs_ceph_new.c

## Purpose
`vfs_ceph_new.c` is a newer Samba CephFS VFS backend built around dynamically loaded libcephfs low-level APIs. Compared with `vfs_ceph.c`, it keeps explicit Ceph inode and file-handle references in Samba fsp extensions, supports optional proxy lib loading, optional fscrypt key setup through keybridge, optional native Ceph async I/O, and caches share capability details such as case-sensitivity behavior.

## Important APIs, types, and functions
- `struct vfs_ceph_config` stores module configuration, mount/cache pointers, dynamic library handle, cached capabilities, and function pointers loaded with `dlsym()`.
- `enum vfs_cephfs_proxy_mode` and `enum vfs_cephfs_fscrypt_mode` parse `ceph_new:proxy` and `ceph_new:fscrypt`.
- `vfs_cephfs_load_lib()` loads `libcephfs_proxy.so.2` or `libcephfs.so.2` and resolves all required high-level and low-level Ceph symbols.
- `cephmount_*` helpers maintain a refcounted mount cache keyed by config file, user id, and filesystem, with a synthetic debug fd index.
- `vfs_ceph_load_config()`, `vfs_ceph_connect()`, and `vfs_ceph_disconnect()` parse config, load the library, mount/reuse CephFS, optionally configure fscrypt, and clean up.
- `struct vfs_ceph_iref` wraps `Inode *` ownership, while `struct vfs_ceph_fh` wraps directory state, `UserPerm`, `Fh *`, inode ref, debug fd, open flags, and cached dirent memory as a VFS fsp extension.
- `vfs_ceph_ll_*` helpers wrap low-level Ceph inode, lookup, open, create, read/write, xattr, link, rename, statfs, and setattr APIs.
- `vfs_ceph_aio_state` and AIO helpers either submit native `ceph_ll_nonblocking_readv_writev()` when available or fall back to posted synchronous calls with profiling metadata.
- `vfs_ceph_check_case_sensitivity()` reads `ceph.dir.casesensitive` from the share root and caches Samba filesystem capability bits.
- The final `ceph_new_fns` table registers a broad VFS surface under `ceph_new`.

## Control flow
Startup parses share parameters, optionally fetches an fscrypt key from varlink keybridge, dynamically loads libcephfs symbols, and obtains or creates a cached mount. File open resolves the parent directory to an inode reference, allocates an fsp extension with a Ceph `UserPerm`, then either creates a new low-level file or looks up and opens an existing inode. `O_PATH` pathref opens can skip `ceph_ll_open()` and keep only the inode reference. Close releases `Fh *`, owned `Inode *`, `UserPerm`, and cached dirent memory through the fsp-extension destructor.

Most VFS operations fetch the relevant `vfs_ceph_fh` from `files_struct` or resolve a temporary `vfs_ceph_iref`, call a `vfs_ceph_ll_*` helper, then convert `-errno` with `status_code()`/`lstatus_code()`. Directory reads use the `vfs_ceph_fh` itself as the `DIR *` carrier and fill a reusable `struct dirent`. Path-based stat/lstat and pathref xattrs resolve inode references by walking names, while fd-based operations use the stored low-level handle and user permission. DFS referrals are implemented as Ceph symlinks containing `msdfs:` targets.

## State and persistence behavior
Durable state lives in CephFS: files, directories, symlinks, xattrs, ACL xattrs, timestamps, DOS EA attributes, and optional fscrypt policy on the share root. In-process state includes a refcounted mount cache, per-share loaded library/config, cached share capabilities, optional tevent threaded context for async I/O, optional keybridge/fscrypt key data, and per-fsp Ceph handles. Debug fds are synthetic numbers only and are not OS file descriptors.

## Dependencies and integration points
The module integrates with Samba VFS, talloc, tevent, smbd profiling, loadparm, POSIX ACL xattr helpers, DFS helpers, base64 utilities, optional varlink keybridge, optional Linux fscrypt headers, and dynamically loaded libcephfs symbols. It is registered in `wscript_build` as `vfs_ceph_new` and can use either normal libcephfs or the CephFS proxy library depending on `ceph_new:proxy`.

## Risks and edge cases
- Dynamic symbol loading makes startup sensitive to libcephfs/proxy ABI availability; missing any required symbol disables the module.
- Mount cache and config lifetimes are complex: cached mounts can outlive individual `vfs_ceph_config` objects, while fsp extensions keep config pointers.
- Native async completion handles orphaned requests by reparenting state to `NULL`; incorrect cleanup could leak state or complete freed requests.
- `vfs_ceph_ll_walk()` rewrites paths relative to the current Ceph cwd because `ceph_ll_walk()` does not honor absolute paths as expected.
- Case-sensitivity is cached from the share root and assumes administrators do not override it deeper in the tree.
- fscrypt setup lacks strong key validation and applies policy to the connect path when configured.
- Like the legacy module, sendfile/recvfile/sharemode/lease support is limited or unsupported.

## Test signals
No direct tests were found in this subset. Validation should cover library/proxy loading modes, mount cache reuse/refcounting, low-level open/create/O_PATH paths, directory iteration, stat/btime and case-sensitivity xattr capabilities, xattr/DOS/ACL behavior, DFS symlink referrals, strict allocation, optional native async reads/writes, fscrypt keybridge policy setup, and teardown with open handles. Build registration in `wscript_build` is the static integration signal.
