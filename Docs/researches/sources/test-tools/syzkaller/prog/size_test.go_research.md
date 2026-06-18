## sources/test-tools/syzkaller/prog/size_test.go

Purpose: verifies automatic length and offset assignment for many syzlang patterns.

Important APIs/types/functions: `TestAssignSizeRandom` and `TestAssignSize`.

Control flow: random tests generate and mutate programs, reassign sizes, and ensure serialization remains stable or at least valid. Table tests deserialize specific programs, apply `assignSizesCall`, and compare serialized output with expected length/offset values.

State and persistence: in-memory programs only.

Dependencies/integration: uses `TestDeserializeHelper`, test target descriptions, serialization, mutation, and generated calls.

Risks: table expectations are tightly coupled to test target descriptions and serialization. The table is intentionally broad because length paths are easy to regress.

Test signals: very strong coverage for `LenType` semantics, including nested parents, syscall refs, VMAs, arrays, unions, offsets, and ANY squashing.
