# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_kshare.c

This file manages kernel-side SMB share lifecycle for the illumos SMB server. It bridges userland share definitions, door upcalls, server export state, AVL-backed share lookup, and asynchronous unshare cleanup.

Key responsibilities:
- Initializes and destroys global share/unexport kmem caches.
- Starts and stops per-server share export state.
- Maintains `sv->sv_export.e_share_avl`, an AVL tree of `smb_kshare_t` objects using `smb_avl_*` helpers from `smb_kutil.c`.
- Exports built-in transient shares: `IPC$`, `c$`, and `vss$`.
- Decodes userland nvlist share definitions into kernel `smb_kshare_t`.
- Handles autohome reference counting and special/admin share flags.
- Resolves disk-share roots through `smb_server_share_lookup`.
- Handles continuous availability share setup through `smb2_dh_new_ca_share`.
- Queues unexport events to `e_unexport_thread` so disconnect/cleanup work is decoupled from ioctl or unmount contexts.
- Provides host access filtering by upcalling to `smbd`.

Important functions:
- `smb_export_start` creates the share AVL and publishes transient shares.
- `smb_export_stop` flips export readiness off and destroys the AVL.
- `smb_kshare_export_list` unpacks an nvlist of shares from ioctl data and exports each decoded share.
- `smb_kshare_unexport_list` unexports shares, then queues asynchronous server unshare cleanup.
- `smb_kshare_lookup` returns a held share object; callers must release with `smb_kshare_release`.
- `smb_kshare_export` handles duplicate/autohome logic, root-node lookup, AVL insertion, and CA setup.
- `smb_kshare_unexport` removes a share from the AVL or decrements autohome count.
- `smb_kshare_decode` maps nvlist properties and SMB share options to `smb_kshare_t` fields and flags.
- `smb_kshare_destroy` releases CA/root nodes and all duplicated strings.
- `smb_kshare_hostaccess` maps share-level host allow/deny/read-only lists into ACE permissions.

Concurrency and lifetime:
- Export readiness is protected by `sv_export.e_mutex`.
- Share objects use `shr_refcnt` and `shr_mutex`; AVL callbacks increment/decrement references.
- AVL destruction waits for in-flight AVL users through `smb_avl_destroy`.
- Unexport cleanup is intentionally asynchronous to avoid deadlocks during forced unmount or stuck filesystem operations.
- `smb_kshare_export` consumes ownership of `shr` only on success; callers destroy it on failure.

Filesystem relevance:
- Disk shares hold a root `smb_node_t` for the shared path.
- Unexport paths call `smb_server_unshare` asynchronously, which disconnects trees/files associated with the share.
- CA shares may create or import persistent handle directories.

Edge cases and risks:
- ioctl nvlist size is checked against the ioctl buffer length before unpacking.
- `smb_kshare_decode` relies on required nvlist fields `name`, `path`, `smb`, and `type`; malformed definitions fail decode.
- OEM share names longer than `SMB_SHARE_OEMNAME_MAX` become `NULL` and are skipped by RAP enumeration.
- Autohome shares are treated specially: duplicate export increments `shr_autocnt`; unexport removes only when count reaches zero.
- Door upcall code is marked non-thread-safe and expects caller serialization.
