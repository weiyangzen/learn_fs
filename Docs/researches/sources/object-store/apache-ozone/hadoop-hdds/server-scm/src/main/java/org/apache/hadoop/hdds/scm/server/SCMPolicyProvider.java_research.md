# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMPolicyProvider.java

Purpose: `SCMPolicyProvider` supplies Hadoop service authorization mappings for SCM RPC protocols. RPC servers use it when Hadoop security authorization is enabled.

Important APIs and types: It extends `PolicyProvider`. `getInstance()` returns a memoized singleton. `getServices()` returns ACL-key/protocol pairs for datanode protocol, container-location protocol, block-location protocol, SCM security protocol, secret-key protocols for OM/SCM/datanode, and reconfiguration protocol.

Control flow: There is no complex flow. RPC servers call `SCMPolicyProvider.getInstance()` and pass it to `refreshServiceAcl`; Hadoop authorization then evaluates configured ACLs per protocol.

State and persistence behavior: The provider owns an immutable static list of service mappings. ACL values are persisted in external Hadoop/Ozone configuration, not in this class.

Dependencies and integration points: It integrates `StorageContainerDatanodeProtocol`, `StorageContainerLocationProtocol`, `ScmBlockLocationProtocol`, `SCMSecurityProtocol`, secret-key protocols, and `ReconfigureProtocol` with Hadoop service authorization.

Risks: New SCM RPC protocols must be added here or service authorization may not protect them correctly. Misconfigured ACL keys can deny legitimate clients or allow unexpected access.

Test signals: Tests should verify singleton reuse, service list contents, ACL key/protocol pairing, and that each SCM RPC server refreshes ACLs with this provider when authorization is enabled.
