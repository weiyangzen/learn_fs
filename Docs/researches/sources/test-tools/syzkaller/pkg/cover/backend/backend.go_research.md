# sources/test-tools/syzkaller/pkg/cover/backend/backend.go

Purpose: Public coverage backend facade and shared data model for symbolization/coverage mapping across ELF, Mach-O, and gVisor backends.

Important APIs/types/functions: `Impl`, `CompileUnit`, `Symbol`, `ObjectUnit`, `Frame`, `Range`, `SecRange`, `LineEnd`, `Make`, and `GetPCBase`.

Control flow: `Make` derives kernel dirs, target, module object paths, and VM type from manager config. It requires a kernel object directory, dispatches to `makeMachO` for Darwin, `makeGvisor` for gVisor, and otherwise `makeELF`, optionally passing Android split-build path delimiters. `GetPCBase` returns Linux PC base only for non-gVisor/non-Starnix Linux targets; otherwise 0.

State and persistence behavior: `Impl` holds in-memory compile units, symbols, frames, callback points, precise coverage flag, and a `Symbolize` function. No direct persistence in this file.

Dependencies/integration points: Integrates `mgrconfig`, `vminfo.KernelModule`, and `targets`. Other backend files implement ELF, DWARF, Mach-O, module discovery, and PC helpers.

Risks: Missing `KernelDirs().Obj` fails early. Backend selection is target/VM sensitive; new VM types may need explicit handling in both `Make` and `GetPCBase`. Android delimiter handling is hard-coded to known Pixel path markers.

Test signals: This file is mostly integration glue; backend-specific tests live in adjacent files such as ELF tests, while higher-level coverage flows exercise `Make`.
