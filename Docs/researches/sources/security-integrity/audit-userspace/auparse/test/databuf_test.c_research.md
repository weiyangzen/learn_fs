<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/databuf_test.c -->
# sources/security-integrity/audit-userspace/auparse/test/databuf_test.c

Purpose: unit test for the auparse `DataBuf` helper, covering append, advance, reset, replace, compaction, and head-preservation semantics.

Important APIs and functions: `test_basic` validates `databuf_init`, `databuf_append`, `databuf_beg`, `databuf_advance`, and `databuf_free`; `test_preserve` adds `DATABUF_FLAG_PRESERVE_HEAD`, `databuf_reset`, and `databuf_replace`.

Control flow and state: tests allocate a local `DataBuf`, mutate it through append/consume cycles, and inspect public `len` and `offset` fields plus memory contents with `memcmp`. No persistent files or global state are used.

Dependencies and integration: includes `data_buf.h` and `config.h`. The script notes this binary is built but not run by `run_auparse_tests.sh.in`, so coverage depends on automake test registration elsewhere or manual execution.

Risks and test signals: strong at catching off-by-one and compaction regressions in buffered parsing. Weaknesses are assert-only failures and lack of allocation-failure simulation. Passing prints `databuf tests: all passed`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/databuf_test.c -->
