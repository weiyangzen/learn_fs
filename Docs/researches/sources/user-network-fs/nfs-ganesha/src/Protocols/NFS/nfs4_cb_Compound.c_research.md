<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_cb_Compound.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_cb_Compound.c

## Purpose
Provides helper routines for constructing and freeing NFSv4 callback `CB_COMPOUND` requests sent from the server to clients.

## APIs, Types, and Functions
Exports `cb_compound_init_v4()`, `cb_compound_add_op()`, and `cb_compound_free()`. It uses `nfs4_compound_t`, `nfs_cb_argop4`, `alloc_cb_argop()`, `alloc_cb_resop()`, `free_cb_argop()`, `free_cb_resop()`, and a default tag table containing `"Ganesha CB Compound"`.

## Control Flow, State, and Persistence
Initialization zeroes the compound container, sets minor version and callback identifier, allocates argument and response arrays sized for the planned operation count, and either attaches a caller-provided tag or the static default tag. `cb_compound_add_op()` appends by shallow-copying one callback argument op and increments both argument and response lengths. `cb_compound_free()` releases the allocated op arrays. There is no persistent state beyond the caller-owned callback compound object.

## Dependencies and Integration
Integrated with the NFSv4 callback RPC stack, delegation recall, layout recall, and session backchannel code that needs to compose callback operations. It depends on callback XDR allocation helpers and assumes callers manage any pointed-to data inside shallow-copied ops.

## Risks and Test Signals
Risks include caller-provided tag lifetime, shallow-copy ownership of callback operation payloads, no capacity check in `cb_compound_add_op()`, and mismatched argument/response array lengths if callers over-add. Test signals are callback creation for CB_NULL/CB_RECALL-style operations, bounds tests around planned op count, custom tag lifetime checks, and leak checks after callback failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_cb_Compound.c -->
