## sources/security-integrity/libcap/libcap/cap_test.c

Purpose: built-in C regression executable for core libcap allocation, bit discovery, flag manipulation, launcher allocation, proc-root management, and prctl error behavior.

Important APIs/functions: `test_cap_bits`, `test_cap_flags`, `test_short_bits`, `test_alloc`, `test_prctl`, helper `noop`, and `main`.

Control flow: validates binary-search max-bit logic over sample values, exercises cap flag set/fill/compare/clear behavior, checks text buffer size assumptions, allocates/free-tests `cap_t`, `cap_iab_t`, and launchers including bad-pointer rejection, tests `cap_proc_root()` replacement/free contract, and checks `cap_get_bound(-1)` returns `EINVAL`.

State/persistence: creates and frees libcap heap objects and changes process proc-root global; no kernel state except prctl read.

Dependencies/integration: internal `libcap.h`, public libcap APIs, built by `libcap/Makefile`.

Risks: not exhaustive for file/process mutating APIs; some failure paths return early without freeing every prior allocation in the test itself.

Test signals: `make -C libcap test` expects `cap_test PASS`; failures print named test sections.
