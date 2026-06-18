# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_swn.c

## Purpose

Implements CIFS client integration with the SMB Service Witness Protocol userspace daemon through generic netlink, tracking witness registrations and reacting to resource state changes or client-move notifications.

## Main Responsibilities

- Maintains witness registrations:
  - Global IDR `cifs_swnreg_idr` maps registration IDs to `struct cifs_swn_reg`.
  - `cifs_find_swn_reg()` matches tcons by extracted network and share names.
  - `cifs_get_swn_reg()` reuses or allocates registrations, assigns IDs, stores notify flags, and records the tcon.
  - `cifs_put_swn_reg()` drops references and calls `cifs_swn_reg_release()` on the final put.
- Sends netlink messages:
  - `cifs_swn_send_register_message()` builds `CIFS_GENL_CMD_SWN_REGISTER` messages with registration ID, network name, share name, IP, notify flags, and Kerberos or NTLM authentication info.
  - `cifs_swn_send_unregister_message()` builds unregister messages.
  - `cifs_swn_check()` re-sends register messages for all registrations, used for retry/health checks.
- Handles authentication attributes:
  - `cifs_swn_auth_info_krb()` marks Kerberos auth.
  - `cifs_swn_auth_info_ntlm()` sends username, password, and domain when present.
- Handles notifications:
  - `cifs_swn_notify()` validates registration ID and notification type attributes.
  - Resource changes call `cifs_swn_resource_state_changed()` and trigger reconnect for available/unavailable states.
  - Client-move notifications parse an address and call `cifs_swn_client_move()`.
- Handles witness-directed reconnect:
  - `cifs_swn_reconnect()` stores a new destination address/port, toggles `use_swn_dstaddr`, unregisters old witness state, registers new witness state, and signals cifsd reconnect.
  - `cifs_swn_store_swn_addr()` preserves the old server port when storing the new address.
- Provides `cifs_swn_dump()` for DebugData witness registration reporting.

## Key Data/Control Flow

- Registration identity is network name plus share name extracted from `tcon->tree_name`.
- Scaleout shares enable IP notifications via `SMB2_SHARE_CAP_SCALEOUT`.
- Register messages use the stored SWN destination address if a move/reconnect target is active; otherwise they use the server destination address.
- `cifs_swn_register()` intentionally returns success even if sending the register message fails, because the echo task can retry.
- Reconnect stores the alternate destination while holding the server lock and avoids doing work if the notified address is already the current destination.

## Concurrency and Lifetime Notes

- `cifs_swnreg_idr_mutex` protects the registration IDR, registration lookup, allocation, refcount put, and debug dumping.
- Registrations hold raw `tcon` pointers and assume tcon lifetime is managed by the caller/register-unregister integration.

## Security and Exposure Notes

- NTLM witness registration messages may include username, password, and domain attributes to the userspace daemon.
- Kerberos mode sends only a Kerberos auth flag.
- Notification attributes are validated for presence before use, but the code trusts the registered userspace netlink family path for delivery semantics.
