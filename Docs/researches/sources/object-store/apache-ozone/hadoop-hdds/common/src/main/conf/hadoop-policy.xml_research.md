## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/conf/hadoop-policy.xml

**Purpose:** Provides the default Hadoop service authorization policy file shipped with Ozone/HDDS, listing ACL properties for many Hadoop IPC protocols.

**Important APIs/types/functions:** The file is an XML `<configuration>` with properties such as `security.client.protocol.acl`, `security.client.datanode.protocol.acl`, `security.datanode.protocol.acl`, `security.admin.operations.protocol.acl`, refresh protocols, HA/ZKFC/QJournal protocols, MapReduce history/job protocols, and YARN resource/application/container/localizer protocols. Every listed property defaults to `*`, meaning all users are allowed, with descriptions explaining ACL syntax.

**Control flow:** When Hadoop service-level authorization is enabled and `hadoop.policy.file` points to this file, protocol servers consult these ACL values to decide whether callers may invoke each service.

**State and persistence:** Persistent XML configuration defaults. The values are deployment state when packaged or copied into a configuration directory.

**Dependencies and integration points:** Integrated by Hadoop IPC authorization policy loading and referenced by `OZONE_POLICYFILE` defaults in environment configuration. It affects Ozone components that expose or depend on Hadoop protocols.

**Risks:** The permissive `*` defaults are convenient but insecure for hardened deployments unless overridden. Drift from upstream Hadoop protocol names can leave some protocols unintentionally unrestricted or unconfigured.

**Test signals:** XML parsing and runtime authorization integration are tested elsewhere; this file itself has no direct unit tests in the subset.
