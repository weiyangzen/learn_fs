# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/TestOzoneConsts.java

## Purpose
Tests compatibility of Ozone tenant policy label constants.

## Important APIs, types, and functions
- Uses `OzoneConsts` tenant-policy label constants.
- Test case is `testOzoneTenantPolicyLabelCompatibility`.

## Control flow
The test compares current constants to expected compatibility values.

## State and persistence behavior
No mutable state or persistence.

## Dependencies and integration points
Tenant policy labels may be consumed by external APIs, persisted metadata, or authorization policy integration.

## Risks and test signals
Renaming constants can break compatibility. This test is a direct constant-value guard.
