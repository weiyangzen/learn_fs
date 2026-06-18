# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_device.c

## Summary
Implements core `device_t` accessors, `devhandle_t` comparison/subclass/call lookup, generic device calls, and device property get/set helpers.

## Main Responsibilities
- Provides the global `root_device`.
- Implements `devhandle_is_valid()`, `devhandle_invalid()`, `devhandle_type()`, `devhandle_compare()`, and subclass helpers.
- Looks up device-call descriptors through handle implementations and system-default link sets.
- Exposes common `device_t` accessors for class, cfdata, cfdriver, cfattach, unit, xname, parent, activation, private data, properties, and handle.
- Implements generic device-call dispatch and child enumeration.
- Retrieves properties from the device property dictionary first, then platform device-call backends.
- Provides typed property length/type/encoding/data/string/bool/integer get APIs and typed set/delete APIs.

## Important Behavior
Property lookup treats `ENOENT` from the local dictionary as permission to ask the platform backend. Dictionary-backed properties are native-endian; platform-backed properties must report explicit little or big endian encoding.

String and data properties can be fetched into caller buffers or exact-sized allocated buffers. Integer helpers validate size and range; signed helpers sign-extend smaller two's-complement values before range checks.

## Dependencies
Uses autoconf device internals, device-call link sets, proplib dictionaries/objects, `kmem`, and byte-order constants.

## Risks
`device_set_private()` asserts private data is set exactly once and non-NULL. Property allocation loops can retry if backend property size changes between length query and fetch; backends must set `propsize` correctly, especially on `EFBIG`.
