# sources/test-tools/ior/src/mdtest.h

Purpose: public result interface for mdtest.

Important APIs and types: `mdtest_test_num_t` enumerates the result slots for directory create/stat/read/rename/remove, file create/stat/read/remove, tree create/remove, and sentinel `MDTEST_LAST_NUM`. `mdtest_results_t` stores per-test rates, rates before final barrier, times, times before barrier, item counts, total errors, and stonewall metrics. `mdtest_run()` is the exported benchmark API.

Control flow and integration: callers initialize MPI, pass command-line style arguments, communicator, and output stream to `mdtest_run()`, then inspect the returned array of `mdtest_results_t` entries. The array length is driven by the `-i` iterations option, not encoded in the type.

State and persistence: no direct state in the header. The returned pointer is heap allocated by `mdtest.c`; callers must free it. Result slots are indexed using the enum, so the enum order is an ABI-like contract with summarization code and CSV writers.

Risks: no destructor or result-count field is included. Callers need external knowledge of iteration count. Adding or reordering enum values requires coordinated updates in `mdtest_test_name()`, result summaries, CSV header generation, and consumers.

Test signals: compile against C and C++ consumers, verify enum slot names and result arrays for simple DUMMY backend runs, and check that `total_errors` propagates when verification fails.
