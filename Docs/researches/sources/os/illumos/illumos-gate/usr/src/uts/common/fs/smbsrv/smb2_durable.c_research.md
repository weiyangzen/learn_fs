# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_durable.c

Read completely. This file implements SMB2 durable, resilient, and persistent handle support, including persistent-handle import for continuous-availability shares, nvlist-backed on-disk state, durable reconnect validation, timeout expiration, orphan cleanup, and the resiliency FSCTL.

Durable-handle policy starts with `smb_dh_create_allowed()` and `smb_dh_should_save()`. Durable creation is allowed for files with batch oplocks, handle-caching leases, or persistent v2 requests, and optionally for directories when persistent. Save decisions depend on server/session/user/tree shutdown state, explicit logoff preservation mode, resilient state, persistent state, and whether the open still has suitable batch or handle-caching state.

Persistent handles are stored as share-root named streams with names like `:<persistid>:$CA`. `smb2_dh_new_ca_share()` schedules import work for CA shares. `smb2_dh_import_share()` creates an internal tree connect, scans stream names, reads nvlist state, and calls `smb2_dh_import_handle()`. Import restores the original path, owner SID credential, access/share/options, create GUID, client UUID, lease or oplock state, byte-range locks, lock sequence table, pending sticky times, persistent ID, and orphan durable state.

`smb2_dh_make_persistent()` creates the state stream and initializes fixed nvlist fields. `smb2_dh_update_nvfile()` serializes the nvlist with XDR and writes it to the persistent stream. Update helpers persist oplock/lease state, locks, lock sequences, and sticky timestamps.

Reconnect is handled by `smb2_dh_reconnect()`, with validation in `smb2_dh_reconnect_checks()`: same user, matching lease/client/name rules, v2 persistent flag consistency, and create GUID match. Expiration and shutdown paths are handled by `smb2_durable_timers()`, `smb2_dh_close_my_orphans()`, `smb2_dh_shutdown()`, and internal expire/cleanup callbacks.

`smb2_fsctl_set_resilient()` implements `FSCTL_LMR_REQUEST_RESILIENCY`, setting resilient durable state and timeout for regular files.
