# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMNodeDetails.java

Purpose: SCM-specific extension of generic `NodeDetails`, adding SCM client, block, datanode protocol, and gRPC endpoint metadata.

Important APIs and types: Builder setters define service id, node id, RPC address, Ratis port, gRPC port, HTTP/HTTPS addresses, and protocol server address/key pairs. Getters expose all SCM-specific endpoints, and `getRpcAddressString` returns host:port through Hadoop `NetUtils`.

Control flow: The builder accumulates endpoint fields and `build` creates an immutable `SCMNodeDetails`. The constructor passes common identity/RPC/Ratis/HTTP data to `NodeDetails` and stores SCM-specific fields.

State and persistence behavior: No persistence; values are configuration-derived runtime metadata.

Dependencies and integration points: Built by `SCMHANodeDetails`, used by Ratis peer creation, checkpoint download host/port lookup, protocol server binding, diagnostics, and config key selection.

Risks and test signals: The builder does not validate required fields, so nulls can propagate to later startup failures. Tests should assert endpoint formatting, getter preservation, `toString` coverage, and behavior with unresolved addresses when flexible FQDN support is enabled elsewhere.
