<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/empty.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/empty.go

## Purpose
`empty.go` is a minimal placeholder package file for `pkg/ifuzz/riscv64/generated`. Its comment says it exists to keep builds working when `insns.go` is excluded by build tags.

## Important APIs, Types, And Functions
The file declares only `package generated` and no functions, variables, or types. It contains the normal syzkaller copyright header and no build tag of its own.

## Control Flow
There is no executable control flow. Its value is package existence: when `generated/insns.go` is excluded by `// go:build !codeanalysis`, this file can still provide a compilable package.

## State, Dependencies, Integration, Risks, And Tests
The file has no state, persistence, imports, or runtime side effects. It integrates with Go build constraints and the `pkg/ifuzz` blank import of generated architecture packages. The risk is behavioral absence: under `codeanalysis`, the generated `init()` that registers RISC-V instructions does not run, so code-analysis builds should not assume RISC-V descriptors are registered. Tests are mostly build signals: package compilation with and without the `codeanalysis` tag and import paths that reference `riscv64/generated`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/empty.go -->
