## sources/storage-engines/foundationdb/bindings/flow/Tuple.h

Purpose: declares the tuple and UUID API exposed by the Flow binding.

Important APIs and types: `Versionstamp` aliases `TupleVersionstamp`. `Uuid` validates and compares 16-byte UUID payloads. `Tuple` exposes `unpack`, `append` overloads for tuple/string/int/bool/float/double/UUID/null/versionstamp/nested, `pack`, typed getters, `range`, `subTuple`, and bytewise comparisons. `ElementType` describes decoded item types.

Control flow: users incrementally append items then call `pack`; unpacked tuples allow indexed type inspection and value retrieval. Comparison operators compare packed byte representation to preserve database sort order.

State and persistence: tuple data is arena-backed packed bytes plus element offsets. Packed tuple bytes become stable database key components.

Dependencies and integration points: includes `fdb_flow.h` and `fdbclient/TupleVersionstamp.h`; used by subspaces, directory layer, allocator, and tests.

Risks: API exposes typed getters that throw on wrong type or bad index. Users must choose UTF8 flag correctly for strings because bytes and UTF8 have distinct type codes.

Test signals: unit tests verify versionstamp tuple support and invalid versionstamp sizing; directory tester uses tuple packing as its instruction stack format.
