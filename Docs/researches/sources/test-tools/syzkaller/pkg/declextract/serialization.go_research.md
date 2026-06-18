# sources/test-tools/syzkaller/pkg/declextract/serialization.go

Purpose: `serialization.go` owns final text emission for generated syzkaller descriptions.

Important APIs/functions: `serialize` initializes the output buffer, writes a standard generated header, then calls include, enum, syscall, fileop, netlink, struct, and define serializers. `fmt` is a thin buffer writer. `serializeIncludes`, `serializeDefines`, `serializeSyscalls`, `serializeEnums`, and `serializeStructs` emit concrete syzlang fragments.

Control flow and state: serialization is ordered intentionally: includes and reusable generated helper types first, then enums/syscalls/fileops/netlink/structs/defines. `serializeFileOps` and `serializeNetlink` have side effects beyond writing text: they also record interfaces and may consume dataflow and probe state. Struct serialization skips zero-size structs, chooses `{}` versus `[]` for struct versus union, emits field names and computed syzkaller types, and appends packed/alignment attributes.

Dependencies and integration: all emitted data comes from the shared `context` populated by earlier passes. The header defines `auto_todo`, `auto_union`, and `auto_aligner`, which are referenced by type-lowering code in `declextract.go`, `typing.go`, and `netlink.go`.

Risks: serializer assumes prior passes have already populated `syzType`, return types, suffixed names, sorted lists, and include/define lists. If any earlier pass omits normalization, this file will emit invalid syzlang rather than detecting all issues. There are no local tests; validation is likely downstream syzlang parsing or generated-description compilation.
