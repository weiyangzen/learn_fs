# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMPolicyProvider.java

Purpose: `OMPolicyProvider` supplies Hadoop service authorization mappings for OM RPC protocols. It binds configured ACL keys to protocol interfaces used by client, admin, inter-service, and reconfiguration RPC endpoints.

Important APIs and types: `getInstance()` returns a memoized singleton via Ratis `MemoizedSupplier`. `getServices()` returns an array of `Service` records for `OzoneManagerProtocol`, `OMInterServiceProtocol`, `OMAdminProtocol`, and `ReconfigureProtocol`.

Control flow: there is no dynamic logic beyond singleton construction and array conversion. The service list is statically initialized and reused.

State and persistence: no persistent state. The effective authorization state lives in Hadoop configuration keys `OZONE_OM_SECURITY_CLIENT_PROTOCOL_ACL`, `OZONE_OM_SECURITY_ADMIN_PROTOCOL_ACL`, and `OZONE_SECURITY_RECONFIGURE_PROTOCOL_ACL`.

Dependencies and integration points: consumed by RPC server/security setup when Hadoop service-level authorization is enabled. It depends on Hadoop `PolicyProvider`, `Service`, and OM protocol classes.

Risks: missing a protocol here means service-level authorization may not be enforced for that endpoint. Mapping an endpoint to the wrong ACL key can over-grant or under-grant access. Since the class is private/unstable, changes should track protocol additions.

Test signals: authorization tests should assert the returned services include all exposed OM RPC protocols and that admin/inter-service protocols use admin ACLs while client protocol uses client ACLs.
