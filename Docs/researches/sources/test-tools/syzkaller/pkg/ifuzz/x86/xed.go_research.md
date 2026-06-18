## sources/test-tools/syzkaller/pkg/ifuzz/x86/xed.go

Purpose: optional cgo bridge to Intel XED for external x86 decode validation in tests.

Important APIs/types/functions: build-tagged with `//go:build xed`. C wrapper `xedDecode` initializes a decoded instruction and returns instruction length or XED error text. Go `init` calls `C.xed_tables_init()` and assigns package global `XedDecode = xedDecode`. `xedDecode` maps syzkaller x86 modes to XED machine/address modes.

Control flow: when tests run with `-tags xed` and XED headers/libs are provided, calls to `XedDecode` route to C. Unsupported mode panics; XED decode failure returns `error`.

State and persistence: process-global XED tables and the package global decoder hook are initialized once. No disk persistence.

Dependencies and integration: depends on Intel XED C headers/library, cgo, `unsafe`, and mode constants from the x86/iset stack. Disabled by default because it requires external setup.

Risks: `unsafe.Pointer(&text[0])` requires non-empty input. Build configuration is brittle because include and linker flags must point to XED artifacts. XED disagreement may represent either syzkaller or XED/model mismatch.

Test signals: used only in opt-in full tests; default builds do not exercise this file.
