## sources/user-network-fs/gcsfuse/internal/util/sizeof.go

Purpose: Estimates nested memory footprint for selected gcsfuse data structures without general reflection-heavy traversal.

Important APIs/types/functions: initialized raw sizes for strings/slices; generic `UnsafeSizeOf`; content-size helpers for strings, string slices, maps, `googleapi.ServerResponse`; `NestedSizeOfGcsMinObject`; `NestedSizeOfGcsFolder`.

Control flow: raw size comes from `unsafe.Sizeof(*ptr)`. Content helpers recursively add string contents, map keys/values, slice members, and pointed-to CRC32C values. Nested object functions add raw struct size plus selected dynamic fields.

State and persistence behavior: package init records runtime raw sizes. No persistence.

Dependencies and integration points: supports memory accounting for metadata/cache objects using `gcs.MinObject`, `gcs.Folder`, and Google API responses.

Risks: estimates are convention-based and omit Go runtime/map overhead beyond key/value sizes. `UnsafeSizeOf` on interface pointers returns interface header size, documented as unsafe. Schema changes to `gcs.MinObject` require manual update.

Test signals: `sizeof_test.go` validates raw and content-size arithmetic; benchmarks measure helper overhead.
