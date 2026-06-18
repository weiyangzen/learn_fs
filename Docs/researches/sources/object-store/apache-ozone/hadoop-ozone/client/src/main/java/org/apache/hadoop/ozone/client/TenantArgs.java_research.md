## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/TenantArgs.java

### Purpose
`TenantArgs` encapsulates optional arguments for tenant creation: the backing volume name and whether creation should be forced when the volume already exists.

### Important APIs and Types
The immutable outer class exposes `getVolumeName` and `getForceCreationWhenVolumeExists`. `newBuilder` returns a mutable `Builder` with setters for both fields and `build`.

### Control Flow
`Builder.build()` requires `volumeName` to be non-null and constructs the immutable value.

### State and Persistence Behavior
This is an immutable client argument object. Tenant creation persistence occurs later through `ObjectStore.createTenant`.

### Dependencies and Integration Points
It is passed to `ObjectStore.createTenant(String, TenantArgs)` and then to `ClientProtocol.createTenant`.

### Risks and Edge Cases
Only null is rejected; empty or invalid volume names are left to lower layers. The force flag defaults to false.

### Test Signals
Tests should verify required volume name, default force flag, setter behavior, and propagation into tenant-create request conversion.
