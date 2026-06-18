# sources/storage-engines/sqlite/ext/wasm/api/opfs-common-inline.c-pp.js

## Purpose

This inline include defines `initS11n()`, the shared serialization helper used by OPFS VFS implementations and their async proxy side. It is inlined into each consumer because the async proxy does not load the full API library and because the function closes over a file-local `state` object with nearly identical shape in each OPFS implementation.

## Important APIs and control flow

`initS11n()` lazily initializes and returns `state.s11n`. It builds `TextEncoder`, `TextDecoder`, `Uint8Array`, and `DataView` views over `state.sabIO` at the serialization region described by `state.sabS11nOffset` and `state.sabS11nSize`. The serialization format is compact and single-record: byte 0 is argument count, the following bytes are type IDs, and the remaining bytes are packed data. Supported types are `number` as Float64, `bigint` as BigInt64, `boolean` as Int32, and UTF-8 strings with a 32-bit length prefix.

`state.s11n.serialize(...args)` writes the header, type IDs, and values into the shared buffer. Calling it with no arguments clears the buffer by zeroing the count byte. `state.s11n.deserialize(clear=false)` reads the most recent serialized record and returns an array or `null`; if `clear` is truthy it clears the buffer after reading. In `opfs-async-proxy` builds the helper also installs `state.s11n.storeException(priority, e)`, which conditionally serializes a compact exception message depending on `state.asyncS11nExceptions`.

## State, persistence, dependencies, and risks

The state is transient cross-thread call data in a `SharedArrayBuffer`; it is not persistent filesystem state. Only one serialized dataset exists at a time, so callers must follow the OPFS request/response protocol and avoid overlapping use of the serialization region. Endianness comes from `state.littleEndian`, and metrics counters are conditionally updated when `vfs.metrics.enable` is defined.

Dependencies include a surrounding `state`, optional `metrics`, `performance.now()`, `TextEncoder/TextDecoder`, `DataView` BigInt accessors, and a `toss()` helper. The risks are buffer overflow if future VFS operations exceed `sabS11nSize`, unsupported argument types, accidental concurrent records, and cross-browser BigInt/DataView behavior. Test signals should include round-tripping all supported primitive types, clearing behavior, exception serialization priority, non-ASCII strings, and the OPFS sanity check in `opfs-common-shared.c-pp.js` that serializes and deserializes a string containing `ä`.
