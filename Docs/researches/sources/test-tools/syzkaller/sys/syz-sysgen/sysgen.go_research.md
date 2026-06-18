# sources/test-tools/syzkaller/sys/syz-sysgen/sysgen.go

Purpose: generates syzkaller syscall metadata, registration code, and executor headers from syzlang descriptions and extracted constants.

Important APIs/types/functions: data structs `SyscallData`, `Define`, `ArchData`, `OSData`, `CallPropDescription`, `TemplateData`, `Job`; functions `main`, `processJob`, `generateExecutorSyscalls`, `newSyscallData`, `writeTemplate`, and `writeFile`; templates `registerTempl`, `defsTempl`, and `syscallsTempl`.

Control flow: `main` cleans old generated files, iterates target OSes, parses `sys/<os>/*.txt`, deserializes `.const`, creates per-arch jobs, compiles descriptions concurrently, collects generated descriptors and unsupported consts, records syscall attrs/props via reflection, sorts OS data, and writes `sys/register.go`, `executor/defs.h`, and `executor/syscalls.h`.

State and persistence: writes compressed generated syscall descriptor files under `out/sys`, generated Go registration, and executor headers. It avoids rewriting identical files.

Dependencies and integration points: central bridge between `pkg/ast`, `pkg/compiler`, `prog`, `sys/generated`, and `sys/targets`. Executor C++ build consumes generated headers; Go runtime consumes generated registration.

Risks: generator output is sensitive to target list ordering, const extraction completeness, template formatting, and reflection over syscall attrs/props. Concurrency requires const-file fabrication for test OS before goroutines.

Test signals: no local unit test; the generated code must compile, and `constsAreAllDefined` catches stale constants.
