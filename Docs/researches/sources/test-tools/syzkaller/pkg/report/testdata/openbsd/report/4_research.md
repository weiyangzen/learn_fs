# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/4

Purpose: OpenBSD pool allocator fixture for `pool_do_get` freelist corruption. Expected title is `pool: free list modified: knotepl`.

Important parser APIs and patterns: handled by `openbsdOopses` `panic:` format `panic: pool_do_get: ([^:]+) free list modified`, formatted as `pool: free list modified: %[1]v`.

Control flow: panic starts with `pool_do_get: knotepl free list modified`, enters DDB, and the stack goes through `pool_do_get`, `pool_get`, `kqueue_register`, `sys_kevent`, syscall, and `Xsyscall_untramp`. The fixture includes line wrapping in `sys_kevent+0x\n207`, which tests robust frame parsing.

State and persistence: static fixture preserving allocator page/item/offset fields and executor context. Those values are dynamic and should not affect grouping.

Dependencies and integration: validates OpenBSD pool corruption formatting for allocation (`pool_do_get`) versus free paths (`pool_p_free`, `pool_do_put`).

Risks: line wrapping can disrupt frame parsing. Regex ordering must keep this specific pool title before generic panic fallback.

Test signals: exact title `pool: free list modified: knotepl`; stack includes `pool_do_get` and `kqueue_register`.
