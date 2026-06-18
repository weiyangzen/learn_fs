# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_property.c

Runtime FTL property registry and JSON-RPC dump/decode/set support.

Behavior:
- Properties are stored in a per-device LIST.
- Registration rejects duplicate names and aborts on allocation failure.
- Dump emits device name and visible properties, including units/descriptions and read-only marker.
- Verbose-only properties are hidden unless `dev->conf.verbose_mode`.
- Decode allocates an output buffer sized to the property, checks access, and invokes the property decoder.
- Set checks access and invokes the property-specific setter.
- Provides bool/uint dump helpers, generic binary-copy setter, and bool string decoder.

Risk:
- Property names are not copied; registered name/unit/description strings must outlive the property.
- `ftl_properties_deinit()` frees `dev->properties` but does not null it.
