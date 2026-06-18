# sources/test-tools/strace/bundled/linux/include/uapi/linux/ioam6_genl.h

Purpose: defines the IPv6 IOAM generic netlink family ABI for namespace and schema management plus trace event reporting.

Important APIs/types/functions: exports `IOAM6_GENL_NAME`, version, command enum values for adding/deleting/dumping namespaces and schemas, namespace-to-schema binding, command attributes such as namespace ID/data and schema ID/data, and event attributes for IOAM trace notifications.

Control flow: userspace sends generic netlink commands to create namespaces, attach schema data up to `IOAM6_MAX_SCHEMA_DATA_LEN`, list configured objects, and receive multicast trace events from `IOAM6_GENL_EV_GRP_NAME`.

State/persistence behavior: namespace and schema commands mutate kernel IOAM configuration. Event messages are transient observations of traced packets and do not persist.

Dependencies/integration: no included dependencies beyond enum constants; semantically integrates with generic netlink, IPv6 IOAM encapsulation, and route/tunnel configuration using IOAM state.

Risks and test signals: schema data is variable binary data with a documented maximum. Tests should validate generic netlink family/command names, nested binary attribute formatting, namespace/schema lifecycle commands, and event-group trace decoding.
