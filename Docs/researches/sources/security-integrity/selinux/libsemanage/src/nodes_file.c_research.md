# sources/security-integrity/selinux/libsemanage/src/nodes_file.c

Purpose: text backend for local `nodecon` records.

Important functions: `node_print`, `node_parse`, `SEMANAGE_NODE_FILE_RTABLE`, `node_file_dbase_init`, and release. Format is `nodecon <ipv4|ipv6> <addr> <mask> <context>`.

Control flow: parser verifies header, maps protocol string to `SEMANAGE_PROTO_IP4/IP6`, sets protocol, parses address and mask using protocol-aware setters, parses a non-NULL context, and requires clean trailing parse state. Printer retrieves address and mask strings, converts context to string, and emits one line.

State/persistence: used by `dbase_file` for local node stores. Dependencies include parse utilities, node record wrappers, context conversion, and database file backend.

Risks: invalid protocol/address/mask/context aborts the record; `<<none>>` is rejected. Tests should cover IPv4, IPv6, invalid protocol, invalid netmask for protocol, missing context, comments/blank lines, and round-trip serialization.
