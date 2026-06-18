# sources/test-tools/syzkaller/executor/_include/flatbuffers/verifier.h

Purpose: This FlatBuffers runtime header verifies that an untrusted FlatBuffer is within bounds, aligned, structurally sane, and not too deeply nested before generated accessors interpret it.

Important APIs and types: `Verifier::Options` configures `max_depth`, `max_tables`, `check_alignment`, `check_nested_flatbuffers`, `max_size`, and debug assertion behavior. `Verifier` exposes `Check`, range `Verify`, `VerifyAlignment`, typed `Verify<T>`, `VerifyFromPointer`, `VerifyFieldStruct`, `VerifyField`, `VerifyTable`, vector overloads of `VerifyVector`, `VerifyString`, `VerifyVectorOrString`, `VerifyVectorOfStrings`, `VerifyVectorOfTables`, `VerifyTableStart`, `VerifyBufferFromStart`, `VerifyNestedFlatBuffer`, `VerifyBuffer`, `VerifySizePrefixedBuffer`, `VerifyOffset`, `VerifyComplexity`, `EndTable`, `GetComputedSize`, and FlexBuffers reuse tracker accessors.

Control flow and state: Verification is fail-fast through `Check`. Range validation uses `elem_len < size_ && elem <= size_ - elem_len` to avoid overflow while ensuring in-buffer access. Table verification checks the signed vtable offset, validates vtable size and alignment, increments complexity counters, and relies on generated `T::Verify` to walk fields. Nested buffers instantiate a child verifier with the same options. Optional tracking records an upper bound for computed size.

Dependencies and integration points: It depends on FlatBuffers scalar, offset, vector, identifier, and generated table verification APIs. Generated code calls it for root buffers, tables, vectors, strings, unions, and nested buffers.

Risks and test signals: Risks concentrate around integer overflow in vector byte-size calculations, signed-to-unsigned offset checks, recursion accounting, null pointer handling, and string terminator validation. Tests should cover malformed offsets, self-referential offsets, truncated strings, invalid vtables, nested buffer opt-out, 64-bit offsets, alignment disabled/enabled, and maximum table/depth limits.
