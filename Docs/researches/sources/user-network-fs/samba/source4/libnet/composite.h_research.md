<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/composite.h -->
# sources/user-network-fs/samba/source4/libnet/composite.h

Purpose: defines monitor message IDs and the `monitor_msg` structure used by libnet composite operations to report progress.

Important APIs and types: `mon_SamrCreateUser`, `mon_SamrOpenUser`, `mon_SamrQueryUser`, `mon_SamrCloseUser`, `mon_SamrLookupName`, `mon_SamrDeleteUser`, `mon_SamrSetUser`, `mon_SamrConnect`, `mon_SamrOpenDomain`, `mon_LsaOpenPolicy`, `mon_SamrOpenGroup`, `mon_SamrQueryGroup`, network message IDs, masks, and `struct monitor_msg { uint32_t type; void *data; size_t data_size; }`.

Control flow: no executable flow. Composite libnet calls allocate operation-specific message payloads and invoke a caller-supplied monitor callback with these IDs.

State and persistence: monitor messages are transient and generally talloc-owned by the operation state. They do not persist progress beyond the callback.

Risks: IDs are unscoped macros, so collisions or stale payload expectations are possible. `void *data` requires callers to branch correctly on `type`. Test signals include monitor callback coverage for group/user operations and payload size/type consistency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/composite.h -->
