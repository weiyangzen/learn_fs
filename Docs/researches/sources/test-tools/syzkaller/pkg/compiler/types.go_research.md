# sources/test-tools/syzkaller/pkg/compiler/types.go

Purpose: Built-in syzlang type descriptor table. It defines validation, const checks, varlen/zero-size predicates, and generation for all core syzlang types.

Important APIs/types/functions: `typeDesc`, `typeArg`, `namedArg`, kind constants, descriptors `typeInt`, `typePtr`, `typeVoid`, `typeArray`, `typeLen`, `typeConst`, `typeFlags`, `typeVMA`, `typeCsum`, `typeProc`, `typeText`, `typeString`, `typeFmt`, `typeCompressedImage`, `typeResource`, `typeStruct`, `typeTypedef`, helper functions `generateFlagsType`, `getIntAlignment`, `isSquashableElem`, `constOverflowsBase`, `isBitmask`, `genStrings`, `stringSize`, `genDir`, built-in descriptor globals, and `builtinDefs`.

Control flow: `init` registers descriptor names into `builtinTypes` and parses `builtinDefs`. Each descriptor supplies custom checks and `Gen` logic consumed by `check.go` and `gen.go`. `typeStruct` and `typeResource` use init-time closures to break initialization cycles. Arrays can become buffer types, strings compute static or varlen sizes, integer arguments can become const/flags/range types, and resources derive base format from their root base type.

State and persistence behavior: Global built-in descriptor maps and parsed built-in AST are package state. Generated `prog.Type` instances are in-memory only.

Dependencies/integration points: Central to `Compile`; integrates with `ast`, `prog`, and target ABI settings such as pointer size/int64 alignment.

Risks: Descriptor checks are the compiler's ABI contract; small changes can affect all syscall descriptions. Some special cases are target- or legacy-driven, such as `xdp_mmap_offsets` and built-in ANY layouts known by `prog/any.go`. Invalid descriptor registration panics during init.

Test signals: Covered broadly by all compiler tests, type-specific error testdata, fuzz seeds, squashable pointer checks, and full target compilation.
