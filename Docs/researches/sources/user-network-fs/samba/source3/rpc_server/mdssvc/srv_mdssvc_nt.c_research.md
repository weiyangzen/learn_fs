# sources/user-network-fs/samba/source3/rpc_server/mdssvc/srv_mdssvc_nt.c

Purpose: provides the generated-compatible server-side RPC handlers for the mdssvc pipe and bridges DCERPC requests to the common mdssvc engine.

Important APIs and functions: `create_mdssvc_policy_handle()` creates an `mds_ctx` with `mds_init_ctx()` and stores it in a policy handle. `_mdssvc_open()` resolves the requested share, initializes the context, returns a fake `/<share>` path, and treats `NT_STATUS_WRONG_VOLUME` as Spotlight-disabled rather than a hard fault. `_mdssvc_unknown1()` returns fixed status/flags for a valid handle. `_mdssvc_cmd()` validates the policy handle, session SID, effective uid, and fragment limits before calling `mds_dispatch()`. `_mdssvc_close()` frees the `mds_ctx` and closes the policy handle. Server init/shutdown wrappers call `mds_init()` and `mds_shutdown()` before/after generated boilerplate.

Control flow: the client opens mdssvc for a share, receives a policy handle, sends opaque Spotlight command blobs through `_mdssvc_cmd()`, and closes the handle. Invalid empty handles are treated leniently in some methods to match client expectations; non-empty invalid handles set protocol faults.

State and persistence: the policy handle owns the per-share `mds_ctx`; freeing the handle tears down queries, inode map, and VFS connection via mdssvc destructors. Process-level backend state is managed by mdssvc init/shutdown.

Dependencies: generated mdssvc NDR compatibility glue, DCE/RPC server core, policy-handle helpers, global messaging/event contexts, loadparm share lookup/path substitution, security token/SID checks, and smbd globals.

Risks: `_mdssvc_cmd()` relies on effective uid already matching the authenticated mdssvc uid and panics on mismatch. Fragment checks prevent oversize blobs, but mdssvc currently does not implement mdssvc-layer fragmentation. SID equality is enforced against the opening SID to prevent handle reuse across users.

Test signals: tests should cover opening Spotlight-enabled and disabled shares, invalid handles, SID mismatch, oversize blobs, close cleanup, and end-to-end dispatch of a known Spotlight command.
