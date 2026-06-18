# sources/test-tools/syzkaller/sys/targets/targets.go

Purpose: authoritative target matrix and lazy compiler/runtime configuration for all syzkaller OS/architecture combinations.

Important APIs/types/functions: `Target`, `KernelAddresses`, `osCommon`, `Timeouts`, OS/arch constants, `Get`, `GetEx`, global `List`, `oses`, `init`, `initTarget`, `defaultDataOffset`, `initAddr2Line`, `findAddr2Line`, `Timeouts`, `setCompiler`, `replaceSourceDir`, `lazyInit`, `checkFlagSupported`, `splitArch`, `processMergedFlags`, and `getSourceDir`.

Control flow: package init merges OS common defaults into every target, fills architecture defaults, resolves `${SOURCEDIR}` placeholders, applies environment compiler overrides, derives compilers/objdump/build OS, endian, and addr2line discovery. `GetEx` returns a lazily initialized target and can clone an alternate compiler variant. `lazyInit` checks optional flag support concurrently, applies fallbacks, builds C++ flags, and verifies compiler execution outside CI/source-dir cases.

State and persistence: global target definitions and lazy `sync.Once` initialization are in-process state. No files are written, but it probes external binaries and reads environment variables.

Dependencies and integration points: consumed throughout syzkaller by build, executor, manager config, extraction, sysgen, csource, and test code. Integrates with host OS/compiler environment and source-tree variables.

Risks: target constants and compiler flags are high blast-radius; a wrong flag can break executor builds across many tools. Lazy mutation of global `Target` fields requires `sync.Once` correctness. Environment overrides can make results host-specific.

Test signals: broad repository build/test coverage; specific downstream failures appear in syz-extract, sysgen, executor builds, and manager runtime.
