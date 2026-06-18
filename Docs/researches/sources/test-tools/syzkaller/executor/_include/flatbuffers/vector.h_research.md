# sources/test-tools/syzkaller/executor/_include/flatbuffers/vector.h

Purpose: This FlatBuffers runtime header defines read-only and mutable views over vector data already serialized inside a FlatBuffer. It does not own storage; it interprets a length-prefixed byte region and delegates element access through `IndirectHelper`.

Important APIs and types: `VectorIterator` and `VectorReverseIterator` provide random-access-style traversal while returning values through FlatBuffers indirection semantics. `Vector<T, SizeT>` exposes `size`, deprecated `Length`, `Get`, `operator[]`, `GetEnum`, `GetAs`, `GetAsString`, `GetStructFromOffset`, iterators, `Mutate`, `MutateOffset`, `GetMutableObject`, raw `Data`, typed `data`, `LookupByKey`, and `MutableLookupByKey`. `Vector64` aliases a 64-bit length/offset variant. `make_span` and `make_bytes_span` create `flatbuffers::span` views for observable scalar vectors. `VectorOfAny`, `VectorCast`, and `VectorLength` support reflection and nullable vectors.

Control flow and state: `Vector::size` reads `length_` through `EndianScalar`. Element access asserts bounds and calls `IndirectHelper<T>::Read(Data(), i)`, so scalar, struct, string, table, and offset vectors share one surface. Lookup uses `std::bsearch` over serialized elements and compares keys with generated `KeyCompareWithValue`. Mutation writes scalar values or relative offsets back into the backing buffer; no capacity changes are possible.

Dependencies and integration points: It depends on `flatbuffers/base.h`, `flatbuffers/buffer.h`, `flatbuffers/stl_emulation.h`, `IndirectHelper`, endian helpers, generated table key comparators, and generated accessors. It is consumed by generated FlatBuffers code and by `verifier.h` for vector validation.

Risks and test signals: The class assumes the underlying buffer is valid and aligned; safety relies on verifier use before access. Mutation risks include wrong offset arithmetic, mutating non-scalar data through `Mutate`, and exposing spans only when endian-safe. Tests should cover scalar vectors, vectors of offsets, reverse iteration, sorted-key lookup, nullable `make_span`, 64-bit vectors, and mutations followed by verification.
