# sources/test-tools/syzkaller/prog/any.go

Purpose: manages syzkaller's generated `ANY` pointer representation and squashes complex pointer pointees into an `ANYPTRS` array of byte blobs and resource tokens.

Important APIs/types/functions: `anyTypes` caches builtin `ANYPTRS` component types. `initAnyTypes`, `getAnyPtrType`, `isAnyPtr`, `isAnyRes`, `CallContainsAny`, and `ArgContainsAny` identify any pointers/resources. `complexPtr`, `Prog.complexPtrs`, and `Target.isComplexPtr` classify generated complex pointers. `squashPtr`, `squashPtrImpl`, `squashConst`, `squashResult`, `squashGroup`, `squashedValue`, and `ensureDataElem` implement conversion to `ANYBLOB`/`ANYRES*` union elements.

Control flow and state: target initialization locates builtin `ANYPTRS` in `Target.Types` and stores exact type references for later identity comparisons. Squashing mutates a `PointerArg` in place by replacing its type reference and pointee, while preserving total pointee size. Constants become little-endian/native bytes or fixed-width decimal/hex/octal strings; big-endian constants are byte-swapped before storage. Result args are retyped to the matching `ANYRES` resource union option and keep their resource relationship.

Dependencies and integration: relies on builtin compiler-generated type layout, `ForeachArg`/`ForeachSubArg` from `analysis.go`, arg constructors, endian helpers, and resource use tracking. The text parser/serializer understands `ANY=` and the executor writer serializes the squashed result like ordinary pointer data.

Risks: panics protect unsupported bitfields, overlay structs, bad pointer sizes, and size drift. Incorrect builtin ordering would corrupt all `ANY` interpretation. Squashing mutates result arg type refs, so it must preserve resource-use invariants.

Test signals: `any_test.go` checks static/runtime complex-pointer detection and exact squashed serialization, including idempotent double squash and non-squashable inout/overlay/filename cases.
