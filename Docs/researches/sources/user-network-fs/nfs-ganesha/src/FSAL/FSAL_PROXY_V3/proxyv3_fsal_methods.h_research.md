# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/proxyv3_fsal_methods.h

## Purpose
`proxyv3_fsal_methods.h` is the private PROXY_V3 interface shared by the module, RPC transport, NLM, and conversion utilities. It defines the module/export/object data structures and declares all cross-file helper APIs.

## Important APIs, Types, And Functions
`struct proxyv3_fsal_module` embeds the FSAL module and object ops vector, plus global `num_sockets` and `allow_lookup_optimization` config. `struct proxyv3_client_params` stores configured server address, derived sockaddr metadata, display name, discovered mountd/nfsd/nlm ports, and preferred READDIR size. `struct proxyv3_obj_handle` embeds `fsal_obj_handle`, remote `nfs_fh3`, cached `fattr3`, and optional parent pointer. `struct proxyv3_export` embeds `fsal_export`, client params, cached root object, and root handle bytes.

The header declares RPC setup and wrappers, port discovery, NLM locking, NFS/NLM status mapping, POSIX attribute-mask validation, fattr/sattr conversion, and weak-cache-consistency pre/post attr conversion.

## Control Flow
The header enforces the architecture: `main.c` owns FSAL dispatch and object/export lifetime, `rpc.c` owns transport, `nlm.c` owns locking, and `utils.c` owns translation. Other files obtain backend endpoint details through accessors rather than directly reaching into the export in most cases.

## State And Persistence
The declared structures keep only process-local proxy state. Remote file handles are copied into per-object allocations, and export root handle bytes are cached in the export. Parent pointers are optional and may be absent for reconstructed handles.

## Dependencies And Integration Points
The header includes Ganesha FSAL init/types and system socket definitions. It exposes the global `PROXY_V3` symbol used by module init and RPC buffer sizing. It also publishes conversion helpers that are tightly coupled to generated NFSv3/NLM typedefs.

## Risks
The optional parent pointer is `const` but points to separately allocated object handles whose lifetime is not explicitly refcounted by the child. `root_handle` is fixed at `NFS3_FHSIZE`, so callers must validate lengths before copying. Cross-file APIs rely heavily on `op_ctx` for export and credentials, which makes unit testing require a realistic Ganesha context.

## Test Signals
Compile all PROXY_V3 files together with strict warnings to catch signature drift. Unit-style tests should allocate/release handles and verify fh3 deep-copy ownership, parent pointer behavior for `".."`, and conversion helper prototypes against generated XDR types.
