# sources/test-tools/syzkaller/pkg/compiler/attrs.go

Purpose: Defines syzlang attribute descriptors and parsing metadata for structs, unions, fields, and syscalls.

Important APIs/types/functions: `attrDescAttrType`, `attrDesc`, predefined descriptors such as `attrPacked`, `attrVarlen`, `attrSize`, `attrAlign`, `attrIn`, `attrOut`, `attrInOut`, `attrOutOverlay`, `attrIf`, maps `structAttrs`, `unionAttrs`, `structFieldAttrs`, `unionFieldAttrs`, `callAttrs`, and helpers `initCallAttrs`, `structOrUnionAttrs`, `structOrUnionFieldAttrs`, `makeAttrs`.

Control flow: Package init reflects over `prog.SyscallAttrs` to create syscall attribute descriptors. Additional init-time checks are attached for `size` and `align` attributes. The compiler later consumes these descriptors through `parseAttrs` and related checks/generation.

State and persistence behavior: Global immutable descriptor maps form compiler state. No persistence.

Dependencies/integration points: Depends on `pkg/ast` and `prog`. Attribute descriptors are used by `check.go`, `consts.go`, and `gen.go` to validate and generate syscall/type metadata.

Risks: Reflecting `prog.SyscallAttrs` means adding a new unsupported field kind will panic at init. Attribute name conversion relies on `prog.CppName`, so renames can affect source syntax.

Test signals: Covered indirectly by compiler testdata, attribute validation errors, and generation tests for syscall/field attributes.
