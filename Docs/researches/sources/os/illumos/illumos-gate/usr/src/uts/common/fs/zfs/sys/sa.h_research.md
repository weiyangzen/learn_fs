# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/sa.h

This public header declares the System Attributes (SA) interface used to pack typed object attributes into DMU bonus and spill buffers.

Core definitions:
- `sa_bswap_type_t` enumerates supported byteswap formats: uint arrays of 64/32/16/8 bits and ACLs.
- `sa_attr_type_t` is a 16-bit attribute ID.
- `sa_attr_reg_t` describes an attribute name, fixed length, byteswap class, and assigned ID.
- `sa_data_locator_t` callbacks can locate or synthesize attribute data for update paths.
- `sa_bulk_attr_t` carries attribute descriptors for bulk lookup/update/replace, with private fields filled by SA internals.
- `SA_ADD_BULK_ATTR()` appends a bulk descriptor and increments the caller's index.
- `sa_handle_type_t` selects shared vs private SA handles.

Public API surface:
- Handle acquisition from object or existing dbuf, handle destruction, dbuf hold/release, userdata accessors, lock/unlock helpers.
- Single and bulk lookup/update/remove/size operations.
- Callback-based update, object info/size queries, spill prediction, setup/teardown, replace-all-by-template, SA enablement, cache init/fini, and SA object configuration.
- Kernel-only `sa_lookup_uio()` and `sa_add_projid()` support ZPL-specific paths.

Risk-sensitive invariants:
- Attribute IDs and registered byteswap classes are persistent compatibility surface.
- Transactions must be supplied for mutating operations and must follow DMU transaction rules.
- Bulk descriptors are opaque except through the provided macro and APIs.
