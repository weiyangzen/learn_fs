# sources/test-tools/syzkaller/pkg/compiler/gen.go

Purpose: Generates `prog` resources, syscalls, types, layouts, fields, padding, and expressions from checked syzlang ASTs.

Important APIs/types/functions: `sizeUnassigned`, `genResources`, `genResource`, `collectCallArgSizes`, `getCallName`, `genSyscalls`, `genSyscall`, `typeProxy`, `generateTypes`, `layoutTypes`, `layoutType`, `layoutArray`, `layoutUnion`, `layoutStruct`, `layoutStructFields`, `finalizeStructFields`, bitfield helpers, `genPad`, `genFieldArray`, `genFieldDir`, `genField`, `wrapConditionalField`, `genType`, `genExpression`, `genValue`, `genCommon`, `genIntCommon`, `genIntArray`, and `genStrArray`.

Control flow: Resource generation follows base-resource chains. Syscall generation first computes consistent syscall argument sizes across variants, generates calls, then marks pointer elements squashable after all recursive types exist. Type generation replaces concrete types in syscalls with deterministic `prog.Ref` indices. Layout recursively computes array/struct/union sizes, alignment, padding, overlays, and bitfields. Conditional fields are wrapped as anonymous unions with a `void` alternative.

State and persistence behavior: Mutates generated `prog.Type` objects, compiler `structTypes`, and synthetic conditional wrapper entries in memory. No disk persistence.

Dependencies/integration points: Uses `prog`, `serializer`, checked compiler state, type descriptors from `types.go`, and attributes from `attrs.go`. Output feeds syzkaller program generation/mutation.

Risks: Layout logic is dense and architecture-sensitive. Bitfield offset/unit-size handling has panic guards for unexpected states. `collectCallArgSizes` must keep syscall variants ABI-compatible. Conditional wrapping rewrites value paths by prepending parent references, which is easy to regress.

Test signals: Covered by compiler all-target tests, canned data, alignment tests, flatten flag tests, and squashable pointer tests.
