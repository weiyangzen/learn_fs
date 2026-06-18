## sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_helper.c

### Purpose
`fsal_helper.c` implements common high-level FSAL operations used by protocol layers and cache layers. It wraps low-level object methods with NFS/FSAL policy: credential checks, create ownership rules, setattr semantics, path walking, cross-junction readdir behavior, delegation conflict handling, synchronous I/O wrappers, RDMA read buffer handling, and xattr list encoding.

### Important APIs, Types, And Functions
Permission helpers include `fsal_not_in_group_list`, `check_open_permission`, `fsal_check_create_owner`, and `fsal_check_setattr_perms`. Main operation helpers include `open2_by_name`, `fsal_setattr`, `fsal_readlink`, `fsal_link`, `fsal_lookup`, `fsal_lookup_path`, `fsal_lookupp`, `fsal_create_set_verifier`, `fsal_create`, `fsal_create_verify`, `fsal_readdir`, `fsal_remove`, `fsal_rename`, `fsal_open2`, `fsal_reopen2`, `fsal_statfs`, `fsal_verify2`, `get_optional_attrs`, `get_buffer_for_io_response`, `fsal_read2`, `fsal_read`, `fsal_write`, `fsal_listxattr_helper`, and `fsal_close2`.

### Control Flow
Open-by-name validates the parent directory, rejects dot entries, checks lookup permission, calls the FSAL `open2` method, and if requested performs a post-open permission check with cleanup close on failure. `fsal_setattr` rejects bad truncates, checks delegations, verifies time-setting support, computes required ACL/mode permissions, applies Linux-like setuid/setgid clearing, and calls `setattr2`. Lookup and path walking enforce directory execute permissions, prohibit `..` in full paths, and hold/release object references while walking through MDCACHE. `fsal_create` normalizes owner/group attributes, dispatches by object type, closes regular files opened only for create, and handles `ERR_FSAL_EXIST` by lookup/type verification. Readdir checks list and attribute permissions, invokes object `readdir`, and `populate_dirent` handles cross-junction attributes by temporarily switching export context. Remove and rename protect junction/export roots, check delegation conflicts, close objects before unlink, optionally mark preserved unlinks with open states, and delegate to object operations. Synchronous read/write call async operations and wait on a condition variable, repeating while `fsal_resume` is set.

### State And Persistence
The helpers primarily mutate operation-local structs, but also rely heavily on `op_ctx` for credentials, export context, RDMA state, and unlink-with-states state. Reference counts on object handles and exports are acquired and released during lookup, readdir junction traversal, and close/error paths. The file does not persist data beyond the backend operations it invokes.

### Dependencies And Integration Points
It integrates protocol layers with FSAL object/export vectors from `default_methods.c` and FSAL implementations. It uses `nfs_exports`, `nfs4_acls`, SAL state/delegation functions, `fsal_convert`, RDMA request structures when enabled, and `nfs_param` runtime configuration. The helpers expect object methods to honor reference and callback contracts.

### Risks
Correctness is sensitive to reference balance on error paths, especially cross-junction readdir and path walking. Permission logic depends on accurate current attributes and ACL availability; missing ACLs intentionally deny some non-owner setattr paths. `fsal_create` temporarily modifies `attrs->valid_mask` and restores it, so early returns must preserve caller expectations. Synchronous I/O waits rely on callbacks always firing. `fsal_listxattr_helper` parses flat xattr buffers and has subtle cookie/length behavior; malformed non-NUL-terminated lists or size limits can expose edge bugs. RDMA buffer selection asserts that requested size fits `data_chunk_length`.

### Test Signals
Tests should cover non-root owner/group create and setattr cases, setuid/setgid clearing, exclusive-create verifier replay, lookup of dot/dotdot/root, path traversal with repeated slashes and `..`, cross-junction readdir success and stale-junction failure, remove/rename of junctions and delegated objects, preserved unlink state marking, RDMA and allocated read buffers, synchronous read/write resume, optional attrs with `ATTR_RDATTR_ERR`, and xattr cookie/maxbytes edge cases.
