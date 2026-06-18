# sources/test-tools/syzkaller/sys/syz-extract/netbsd.go

Purpose: NetBSD backend for constant extraction.

Important APIs/types/functions: `netbsd.prepare`, `netbsd.prepareArch`, `machineLink`, `machineInclude`, and `netbsd.processFile`.

Control flow: requires `-build`; `prepareArch` symlinks NetBSD arch include directories into the build dir. `processFile` constructs NetBSD kernel include flags, augments requested constants with compatibility names for syscall and Linux-compat prefixes, runs `gcc`, then maps successful compatibility values back to original names.

State and persistence: creates build-dir symlinks; mutates `info.Consts` locally by appending compatibility probes.

Dependencies and integration points: relies on NetBSD source layout, GCC, compiler const metadata, and shared `extract`.

Risks: compatibility-name generation mutates the const info slice and assumes later consumers do not reuse it in a conflicting way. Only known prefix/suffix patterns are covered.

Test signals: no direct extractor tests; generated constants and NetBSD target tests catch downstream failures.
