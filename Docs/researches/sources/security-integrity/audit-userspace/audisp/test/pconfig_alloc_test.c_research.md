# sources/security-integrity/audit-userspace/audisp/test/pconfig_alloc_test.c

Purpose: Tests allocation-failure handling in the audisp plugin configuration parser.

Important APIs, types, and functions: Defines replacement allocators (`test_malloc`, `test_calloc`, `test_realloc`, `test_strdup`) controlled by `reset_allocs()` and `should_fail()`. It stubs `audit_msg` via `test_audit_msg`, then includes `../audispd-pconfig.c` directly with allocator and logging macros remapped. Test functions are `test_path_preserves_old_value()`, `test_args_preserves_old_value()`, and `test_nv_split_realloc_failure()`.

Control flow: Each test initializes parser state, injects a deterministic failure at a specific allocation count, calls a parser helper (`path_parser()`, `args_parser()`, or `nv_split()`), and asserts that old config values or output invariants remain valid. `main()` runs all three tests through plain `assert()`.

State and persistence: Test state is in the global allocation counters. There is no persistence. Parser objects are initialized with `clear_pconfig()` and cleaned with `free_pconfig()` where applicable.

Dependencies and integration points: Direct inclusion of `audispd-pconfig.c` gives access to static parser helpers but tightly couples the test to implementation internals. It uses `plugin_conf_t`, `struct nv_pair`, and parser functions from the included file.

Risks and edge cases: Because failures are triggered by allocation ordinal, implementation changes that add or remove allocations can require test updates even if behavior remains correct. Direct source inclusion can also mask integration issues caused by different compilation units or macros. The test is valuable because it checks that failed updates preserve old live config instead of partially overwriting it.

Test signals: Built as `pconfig-alloc-test` by `audisp/test/Makefile.am`. Passing this test signals that important parser allocation-failure paths are non-destructive and clean their partially built output.
