# File Research: sources/virtualization/spdk/lib/iscsi/init_grp.h

Initiator-group type and management API header. It defines list entries for initiator names and initiator netmasks, both sized from the iSCSI connection/name constants, and `spdk_iscsi_init_grp`, which stores counts, TAILQ heads, a reference count, a numeric tag, and linkage into the global initiator-group list.

The exported API covers creation from caller-provided name/netmask arrays, adding and deleting initiator entries from existing groups, registering/unregistering groups in the global registry, lookup by tag, destruction, parser entry point, global destruction, and info/config JSON output. This header ties access-control group code to `iscsi/iscsi.h` and `iscsi/conn.h` for shared limits and address sizing.

The interface contract is small but central to target authorization: target-node configuration and RPC code can bind target nodes to these groups, while login checks later use the configured initiator names and netmasks to decide access. The `ref` field is declared here but managed by related target-node/configuration code rather than by this header itself.
