# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/22

Purpose: OpenBSD reporter fixture for a pool allocator integrity panic. The expected title is `pool: free list modified: mbufpl`, derived from `panic: pool_p_free: mbufpl free list modified...`.

Important parser APIs and patterns: `ctorOpenbsd` builds a BSD reporter with `openbsdOopses`. This fixture targets the `panic:` oops format whose title regex is `panic: pool_p_free: ([^:]+) free list modified`, formatted as `pool: free list modified: %[1]v`. Stack symbolization relies on OpenBSD frame text like `pool_p_free(...) at pool_p_free+0x1de`.

Control flow: the raw console starts with the panic, enters DDB, runs `show panic`, `trace`, `show registers`, and later memory/pool diagnostics. The parser should start at the panic, retain enough report text through the OpenBSD crash/debug block, and not let the trailing allocator table change the title.

State and persistence: this is a static golden test fixture. It stores no runtime state, but it preserves volatile pool page, item address, register, process, and allocator statistics to test noisy real-world logs.

Dependencies and integration: integrated with `pkg/report` golden tests for OpenBSD crash detection, title extraction, report boundaries, and frame capture.

Risks: dynamic addresses and long diagnostics can destabilize title extraction if not normalized. Boundary logic must avoid truncating before DDB output while ignoring allocator-table noise for title selection.

Test signals: title should be exactly `pool: free list modified: mbufpl`; the useful stack includes `pool_p_free`, `pool_gc_pages`, and `taskq_thread`.
