## sources/test-tools/syzkaller/prog/size.go

Purpose: assigns and mutates `LenType`/offset arguments based on referenced fields, parent structs, syscall arguments, arrays, VMAs, and bit-size units.

Important APIs/types/functions: `ParentRef`, `SyscallRef`, `Target.assignSizes`, `assignArgSize`, `assignSize`, `foundArg`, `findFieldStruct`, `findArg`, `computeSize`, `assignSizesArray`, `assignSizesCall`, and `randGen.mutateSize`.

Control flow: assignment walks call arguments and nested subargs with parent stacks. For each length arg it resolves the configured path, computes length or offset in units, and writes the constant. `findArg` handles overlays, parents, template-name parent references, and squashed ANY pointers. Mutation intentionally perturbs sizes while avoiding unsupported paths and compressed images.

State and persistence: mutates in-memory `ConstArg.Val` fields. `autos` can restrict which auto-size args are assigned.

Dependencies/integration: depends on `ForeachSubArg` with parent stacks, type metadata, pointer inner args, and mutation generation.

Risks: path resolution panics for invalid descriptions. Squashed ANY pointers leave sizes unchanged. Mutating compressed-image sizes is blocked because decompression assumes valid data.

Test signals: `size_test.go` covers randomized idempotence and a large table of path, parent, syscall, VMA, bit-size, offset, union, and squashed-arg cases.
