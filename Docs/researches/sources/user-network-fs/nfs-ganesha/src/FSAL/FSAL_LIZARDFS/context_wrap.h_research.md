# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/context_wrap.h

Purpose: Declares the credential-aware LizardFS wrapper API used by the LizardFS FSAL implementation.

Important APIs and types: The header includes `fsal_types.h` and `lizardfs/lizardfs_c_api.h`, then declares wrappers for namespace operations, file I/O, metadata, directories, setattr/fsync, links, chunk information, ACLs, and POSIX-style locks. Important data types are `liz_t`, `liz_inode_t`, `liz_entry`, `liz_fileinfo_t`, `liz_attr_reply`, `liz_chunk_info_t`, `liz_acl_t`, and `liz_lock_info_t`.

Control flow: This header forms the abstraction boundary between Ganesha FSAL code and raw LizardFS API calls requiring a user context. Implementation files call `liz_cred_*` functions rather than constructing contexts inline.

State and persistence: No state is declared here. The wrappers pass through pointers to LizardFS instance state, fileinfo objects, ACL objects, and result buffers owned by callers or the LizardFS library.

Dependencies and integration: Included by LizardFS export, handle, ACL, MDS, DS, and internal files. It couples the FSAL directly to the LizardFS C API ABI.

Risks: The header exposes raw LizardFS pointer lifetimes, so callers must know whether returned entries, fileinfo handles, ACLs, and chunk-info arrays need explicit release. Wrapper return conventions mix `int`, `ssize_t`, and pointer returns, which increases error-handling inconsistency. Any LizardFS C API signature change breaks multiple FSAL units.

Test signals: Compile against supported LizardFS library versions, run ABI/header compatibility checks, and exercise each wrapper through its FSAL caller with both success and error paths.
