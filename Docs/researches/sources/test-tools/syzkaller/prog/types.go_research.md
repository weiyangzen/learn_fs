## sources/test-tools/syzkaller/prog/types.go

Purpose: declares syscall metadata, type metadata, expressions, directions, resource descriptions, type traversal, default arguments, and C++ name conversion.

Important APIs/types/functions: `Syscall`, `SyscallAttrs`, `Dir`, `Field`, `Expression`, `BinaryExpression`, `Value`, `BinaryFormat`, `Type`, `Ref`, `TypeCommon`, `ResourceDesc`, `ResourceCtor`, `ResourceType`, integer type family, `LenType`, `ProcType`, `CsumType`, `VmaType`, `BufferType`, `ArrayType`, `PtrType`, `StructType`, `UnionType`, `TypeCtx`, `ForeachType`, `ForeachTypePost`, `ForeachCallType`, `ForeachArgType`, and `CppName`.

Control flow: type-specific methods provide defaults, default checks, string forms, sizes, bitfield metadata, and traversal behavior. Traversal recursively walks pointers, arrays, structs, unions, resources, buffers, and scalar types while tracking direction and optionality and pruning recursive struct/union visits by `(type, dir, optional)`.

State and persistence: type structs are in-memory target description data. `Ref` placeholders exist before `target.restoreLinks` replaces them with actual type pointers.

Dependencies/integration: central contract for compiler-generated descriptions, generation, mutation, validation, serialization, resource analysis, and target init.

Risks: incorrect `DefaultArg` or `isDefaultArg` breaks deserialization defaults and minimization. Traversal pruning must preserve direction/optional distinctions. `TypeCommon.Size` panics for varlen types, so callers must check `Varlen`.

Test signals: package-wide tests cover defaults, traversal effects, length assignment, generation, validation, and serialization.
