<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmTenantArgs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmTenantArgs.java

## Purpose

`OmTenantArgs` stores arguments for creating an Ozone tenant: tenant id, backing volume name, and whether creation should proceed when the volume already exists.

## Important APIs, Types, And Functions

It has direct constructors and a nested `Builder` with `setTenantId`, `setVolumeName`, `setForceCreationWhenVolumeExists`, and `build`. Getters expose `tenantId`, `volumeName`, and the force flag.

## Control Flow, State, And Persistence

The object is immutable after construction. The one-argument constructor defaults the volume name to the tenant id; the builder applies the same default when `volumeName` is unset. Tenant creation persistence happens in OM tenant tables and Ranger policy setup, not in this class.

## Dependencies And Integration Points

It depends on `Objects` and is consumed by `OzoneManagerProtocol.createTenant` and client-side translator code for multitenancy commands.

## Risks And Test Signals

Only `tenantId` is null-checked; validation of legal tenant and volume names is upstream. Tests should cover default volume selection, custom volume selection, force flag propagation, invalid names, and existing-volume behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmTenantArgs.java -->
