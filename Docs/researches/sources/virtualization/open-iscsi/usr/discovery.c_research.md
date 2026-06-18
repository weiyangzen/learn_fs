# File Research: sources/virtualization/open-iscsi/usr/discovery.c

Implements open-iscsi target discovery paths: iSNS, firmware discovery, offloaded SendTargets, and software/kernel-assisted SendTargets.

Major flows:
- `request_initiator_name` asks `iscsid` for configured initiator name and optional alias.
- iSNS support, when compiled, configures server name, registers initiator nodes when required, queries visible targets, and converts portal group objects into `node_rec` entries.
- `discovery_fw` converts firmware boot contexts into node records.
- `discovery_offload_sendtargets` asks `iscsid`/driver offload to perform SendTargets and optionally login, without parsing returned target records.
- SendTargets software flow creates a discovery session, logs in, sends `SendTargets=All`, receives Text Response PDUs, handles continuation via TTT, and parses `TargetName`/`TargetAddress` records.

Session handling:
- `iscsi_alloc_session` creates a discovery session, binds iface data, copies operational parameters, initializes ISID, and configures authentication.
- `iscsi_create_leading_conn` either creates a userspace socket path or kernel IPC/netlink session/connection depending on transport capabilities.
- `iscsi_create_session` performs login, redirect handling, reconnect backoff, kernel parameter setup, connection start, and login-offload waiting.
- Cleanup tears down kernel sessions/connections and transport endpoints.

Parsing details:
- SendTargets data may span PDUs; a `str_buffer` retains partial records.
- IPv6 portal addresses in `[addr]:port,tag` form are handled.
- Missing portal address falls back to the discovery address.
- Records are initialized from default idbm config before discovery fields are filled.
