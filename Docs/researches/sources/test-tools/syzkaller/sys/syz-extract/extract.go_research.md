# sources/test-tools/syzkaller/sys/syz-extract/extract.go

Purpose: command-line driver for extracting syscall constants from OS kernel/header trees into `sys/<os>/*.const` files.

Important APIs/types/functions: defines flags, `Arch`, `File`, `Extractor`, `extractors`, `main`, `worker`, `createArches`, `checkUnsupportedCalls`, `processArch`, and `processFile`.

Control flow: `main` validates flags, resolves OS extractor and arch list, parses syzlang files, prepares source/build trees, fans out arch and file jobs over a channel using `GOMAXPROCS` workers, aggregates per-file/per-arch constants into `compiler.ConstFile`, writes serialized `.const` files, checks unsupported calls, removes temporary build dirs, and exits nonzero on failures.

State and persistence: writes or removes `sys/<os>/<file>.const`; may create temporary build directories when `-build` is used and deletes them after extraction.

Dependencies and integration points: central integration point among `pkg/ast`, `pkg/compiler`, `sys/targets`, OS-specific extractor backends, and `osutil.WriteFile`.

Risks: the shared job channel is never closed, but the main goroutine waits only on known done channels, so leaked worker goroutines are acceptable for a short-lived CLI. Build-dir cleanup only happens after aggregation; early fatal paths can leave temp dirs. Full extraction correctness depends on backend include paths and compiler diagnostics.

Test signals: no direct unit tests here; correctness is usually validated by regenerated `.const` files and subsequent `syz-sysgen`/build failures.
