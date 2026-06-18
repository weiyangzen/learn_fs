# sources/test-tools/syzkaller/sys/syz-extract/fetch.go

Purpose: shared compile-and-fetch engine for `syz-extract` backends.

Important APIs/types/functions: `extractParams`, `extract`, `CompileData`, `compile`, `extractFromExecutable`, `extractFromELF`, and `srcTemplate`.

Control flow: `extract` renders C source for requested constants, compiles it, parses compiler output for undeclared identifiers, retries with missing constants removed, runs the binary or reads an ELF section, and maps values back to constant names. `compile` creates a temp output file, invokes the compiler with stdin source, and returns compiler output on failure.

State and persistence: creates temporary binaries with `osutil.TempFile` and removes successful binaries after extraction. No long-lived state.

Dependencies and integration points: used by every OS-specific extractor. Depends on host compiler behavior, `debug/elf` for object extraction, endian information from `targets.Target`, and syzlang compiler const metadata.

Risks: undeclared parsing is regex-based and compiler-message dependent. Running generated binaries is unsafe for cross-target or incompatible output, so backends use ELF extraction where needed. Empty output maps can hide all constants being undeclared unless checked later.

Test signals: no direct tests here; failures surface as extraction errors or `constsAreAllDefined`/sysgen errors.
