# sources/test-tools/syzkaller/pkg/declextract/entity.go

Purpose: `entity.go` defines the JSON-facing extraction model used by the clang tool and all subsequent declextract passes. It is the schema boundary between extracted kernel facts and generated syzkaller descriptions.

Important APIs/types/functions: `Output` aggregates functions, constants, enums, structs, syscalls, file operations, ioctls, io_uring operations, netlink families, and policies. `Function`, `FunctionScope`, `Field`, `Syscall`, `FileOps`, `Ioctl`, `IouringOp`, `NetlinkFamily`, `NetlinkPolicy`, `NetlinkAttr`, `Struct`, `Enum`, and `Type` model extracted declarations. `TypingFact` and `TypingEntity` model flow edges between returns, arguments, struct fields, locals, and global addresses. `Output.Merge`, `Output.Finalize`, and `Output.SetSourceFile` are the operational methods.

Control flow and state: `Merge` appends another extraction output into the receiver; `Finalize` sorts and deduplicates each top-level slice; `SetSourceFile` rewrites paths and attaches source-file provenance to syscall/fileop/netlink/io_uring entities. It also relaxes static-function status for included `.c` files that are compiled through another translation unit.

Dependencies and integration: consumers in `declextract.go`, `typing.go`, `interface.go`, `fileops.go`, and `netlink.go` mutate hidden fields such as `Field.syzType`, `Syscall.returnType`, `Function.callers`, and resolved `fileOps` callbacks. The public JSON tags are important for stable clang-tool interchange.

Risks: schema changes affect extraction compatibility and generated output determinism. Hidden state means copied values can lose derived metadata if not copied carefully. `EntityGlobalAddr.Name` lacks an explicit JSON tag unlike neighboring fields. There are no local tests for this file; coverage is indirect through end-to-end extraction and serialization paths.
