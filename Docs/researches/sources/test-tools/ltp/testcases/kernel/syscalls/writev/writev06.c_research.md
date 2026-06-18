<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev06.c

Purpose: `writev(2)` regression test that legacy harness test that iovecs pointing to the last readable byte of two mapped pages, each surrounded by `PROT_NONE` mappings, still write two bytes successfully.

Important APIs/types/functions: uses `struct iovec`, `writev()`, file positioning, mmap-protected bad addresses or page-boundary good addresses, and either the legacy `test.h` harness or modern `tst_test` harness depending on the file. Helper routines include signal handlers, `l_seek()` wrappers, fuzzy-sync thread functions, or per-offset validation functions.

Control flow/state: setup builds the file and memory mapping fixture, the main test invokes `writev()` with carefully chosen vectors, and validation checks errno, byte count, file contents, and file offset. Legacy files loop under `TEST_LOOPING`; modern files run once or for a timed fuzzy-sync runtime.

Dependencies/integration: depends on VM fault behavior, generic write path fault-in semantics, and filesystem write semantics. `writev03` requires pthread/librt build flags from the Makefile and a mounted filesystem matrix; `writev07` carries Linux commit tags for iomap partial-write fixes.

Risks/test signals: these tests are sensitive to kernel short-write semantics around invalid iovecs. They intentionally allow both full failure and bounded short write where Linux semantics permit it, but never allow uninitialized data exposure, offset drift, or writes beyond reported byte count.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev06.c -->
