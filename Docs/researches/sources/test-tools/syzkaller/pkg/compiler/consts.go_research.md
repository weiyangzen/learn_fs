# sources/test-tools/syzkaller/pkg/compiler/consts.go

Purpose: Constant extraction and constant patching for syzlang ASTs.

Important APIs/types/functions: `ConstInfo`, `Const`, `ExtractConsts`, `FabricateSyscallConsts`, `constContext`, `extractConsts`, `foreachFieldAttrConst`, `extractTypeConsts`, `addConst`, `constInfo`, `convertConstInfo`, `assignSyscallNumbers`, `patchConsts`, `patchIntConst`, `patchTypeConst`, and `patchConst`.

Control flow: Extraction walks AST integer nodes, directives, defines, syscall numbers, syscall attrs, struct attrs, field conditions, and type arguments. Template instantiation context propagates constants used by template structs to files that instantiate them. Patching copies caller constants, adds built-ins like `PTR_SIZE`, assigns syscall numbers, replaces identifiers with values, removes unsupported flag values, and marks syscalls/declarations unsupported when constants are missing.

State and persistence behavior: Extraction returns per-file `ConstInfo` for external const generation. Patching mutates the cloned AST in memory and records unsupported declarations plus warnings. No direct disk writes.

Dependencies/integration points: Called by `Compile` and `ExtractConsts`; works with `ConstFile` and target syscall-number policy. Uses AST metadata to preserve include/incdir/define associations.

Risks: Missing constants are patched with value 1 to avoid cascading bad ranges, which can hide transitive issues until warnings are reviewed. TODOs note that unsupported dependency pruning is incomplete. Field attribute const extraction currently handles expression attrs only.

Test signals: `consts_test.go`, compiler canned `consts.txt` and `consts_errors.txt`, and full compile tests validate extraction, defines/includes/incdirs, syscall const fabrication, and missing-const handling.
