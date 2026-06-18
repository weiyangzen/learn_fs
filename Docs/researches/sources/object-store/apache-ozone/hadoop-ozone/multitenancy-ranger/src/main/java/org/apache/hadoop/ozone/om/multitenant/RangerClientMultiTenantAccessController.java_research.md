# sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/src/main/java/org/apache/hadoop/ozone/om/multitenant/RangerClientMultiTenantAccessController.java

## Purpose

`RangerClientMultiTenantAccessController` implements `MultiTenantAccessController` by translating Ozone multitenancy policies and roles to Apache Ranger model objects and invoking `RangerClient` over Ranger's admin API.

## Important APIs and Types

- Constructor reads Ranger HTTPS address, Ranger service name, OM Kerberos principal/keytab, or fallback clear-text Ranger admin credentials from configuration, then creates a `RangerClient`.
- Policy methods: `createPolicy`, `getPolicy`, `getLabeledPolicies`, `updatePolicy`, and `deletePolicy`.
- Role methods: `createRole`, `getRole`, `updateRole`, and `deleteRole`.
- `getRangerServicePolicyVersion` fetches service policy version and returns `-1` if Ranger omits it.
- Translation helpers map between Ozone `Policy`, `Role`, `Acl` and Ranger `RangerPolicy`, `RangerRole`, policy resources, policy items, role members, and ACL strings.

## Control Flow

Construction first builds ACL string lookup maps from the interface helper. It requires the Ranger HTTPS URL and service name. If both fallback username and password are configured, it uses SIMPLE auth and treats that username as the OM principal/short name. Otherwise it builds a Kerberos principal by replacing `_HOST` using the OM address hostname, requires a keytab, derives the short user name through `UserGroupInformation`, and creates a Kerberos `RangerClient`. The previous Hadoop login user is restored in a `finally` block after client construction.

Every Ranger operation logs at debug level, invokes the corresponding `RangerClient` call, catches `RangerServiceException`, decodes common HTTP status codes to actionable logs, and rethrows as `IOException`. Policy translation builds Ranger resources for volume/bucket/key if present, maps user and role ACLs into `RangerPolicyItem` entries, and maps labels/description/name/service. Reverse translation reads policy items, converts allowed/denied accesses to Ozone ACLs, assigns them to each role, maps resources by type, warns on unknown resource names, and restores metadata. Role translation handles role ID, name, description, users, createdByUser, nested roles, and role-admin flags.

## State and Persistence

The controller holds a `RangerClient`, Ranger service name, ACL lookup maps, resolved OM principal, and short user name. It does not persist local state. Durable state is in Ranger: policies, roles, memberships, labels, and service policy version.

## Dependencies and Integration Points

It depends on Ozone OM config keys, `OmUtils`, `OzoneConsts.OZONE`, Hadoop security/UGI, Ranger client/model classes, Jersey `ClientResponse.Status`, and the `MultiTenantAccessController` domain model. It is the concrete adapter chosen by `MultiTenantAccessController.create(conf)` when Ranger multitenancy is enabled.

## Risks and Edge Cases

Authentication validity is not checked during construction; invalid credentials surface later as repeated 401 failures. The constructor uses `Objects.requireNonNull`, so missing config becomes `NullPointerException` rather than a typed config error. The policy reverse mapper only reconstructs role ACLs, not user ACLs, even though `toRangerPolicy` emits both user and role items. Unknown ACL strings can map to `null` ACL types. SIMPLE auth requires both username and password; a partially configured fallback silently selects Kerberos and may fail later. `getRangerServicePolicyVersion` returning `-1` for null may hide privilege problems unless callers check it.

## Test Signals

The companion test class creates this controller through the factory with Kerberos-like config but is marked unhealthy because it requires a Ranger endpoint. Strong tests should mock or fake `RangerClient` to verify policy/role conversion, user ACL round-tripping, HTTP status handling, SIMPLE-vs-Kerberos selection, and null policy version behavior without needing live Ranger.
