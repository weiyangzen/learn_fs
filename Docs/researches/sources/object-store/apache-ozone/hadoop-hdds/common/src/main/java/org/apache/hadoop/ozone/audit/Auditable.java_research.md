# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/audit/Auditable.java

## Purpose
`Auditable` marks an entity as able to render itself into key/value pairs for audit logging.

## Important APIs, types, and functions
- `Map<String, String> toAuditMap()` returns values to be logged in audit records.

## Control flow
There is no implementation control flow; each implementing entity chooses which fields to include.

## State and persistence behavior
The interface has no state or persistence. Returned maps are consumed by audit logging code and may become durable logs depending on audit sink configuration.

## Dependencies and integration points
It depends only on `java.util.Map`. Implementations typically use keys from `OzoneConsts` and are consumed by Ozone audit framework components in clients and servers.

## Risks and edge cases
Implementations can leak sensitive data, omit important identifiers, return mutable maps, or use inconsistent key names. Audit consumers should not assume all values are present.

## Test signals
Implementer tests should verify stable audit keys, redaction of sensitive fields, null handling, and consistency with command/action audit expectations.
