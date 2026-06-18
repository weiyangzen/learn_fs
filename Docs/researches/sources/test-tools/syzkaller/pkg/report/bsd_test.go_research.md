# sources/test-tools/syzkaller/pkg/report/bsd_test.go

Purpose: Provides a reusable helper for BSD reporter line-symbolization tests.

Important types and functions: `symbolizeLineTest` holds input and expected line strings. `testSymbolizeLine` constructs a fake symbol table, fake symbolizer callback, invokes a reporter constructor, injects symbols/kernel object, and compares `bsd.symbolizeLine` output against expectations.

Control flow and state: The fake symbolizer recognizes two PCs and returns either a single frame or inline plus outer frames. The helper trims `/bsd/src` build paths through reporter config. Tests using this helper can validate constructor-specific regex matching while sharing symbolization mechanics.

Dependencies and integration: Depends on `mgrconfig.KernelDirs`, `symbolizer.Symbol`, and the report package constructor type `fn`.

Risks: This file defines helper infrastructure but no top-level `Test*` itself in the read section, so actual coverage depends on other platform-specific test files invoking it. Synthetic PC calculation mirrors `bsd.go` assumptions.

Test signals: When invoked by platform tests, it validates file/line insertion and inline frame handling.
