# sources/test-tools/syzkaller/sys/syz-extract/darwin.go

Purpose: Darwin/macOS constant extractor backend for `syz-extract`.

Important APIs/types/functions: implements the `Extractor` interface with `darwin.prepare`, `darwin.prepareArch`, and `darwin.processFile`.

Control flow: prepare hooks are no-ops. `processFile` builds clang include arguments for Darwin kernel source trees (`bsd`, `bsd/sys`, `osfmk`), appends per-description include dirs and `-includedirs`, adds `<sys/syscall.h>`, and calls shared `extract`.

State and persistence: no persistent state; compiles temporary extraction binaries through `fetch.go`.

Dependencies and integration points: relies on clang, Darwin kernel header layout, compiler-extracted const metadata, and the shared extraction template.

Risks: source layout assumptions and TODO around syscall/mach trap sources mean syscall extraction may be incomplete. It prints include dirs to stdout, which can add noisy tool output.

Test signals: no direct tests in this subset; integration coverage comes from running `syz-extract -os=darwin`.
