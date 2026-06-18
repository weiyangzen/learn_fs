<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/util.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/util.c

Source read: complete file, 180 lines, 4458 bytes, sha256 `808d607c5636fec0fa3e6a4f7ab3337302be90ee07bcecbdb31ac0fa96393cc5`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/util.c_research.md`.

Purpose: miscellaneous portability and utility functions for dbench/tbench: shared memory allocation, in-place string substitution, token parsing, timeval math, and millisecond sleep.

Important APIs/types/functions: `shm_setup(size)` allocates zeroed SysV shared memory that survives fork and is marked for deletion; `all_string_sub()` replaces all occurrences of a pattern in a mutable string; `next_token()` parses separator-delimited tokens with double-quote support; `timeval_current()`, `timeval_elapsed()`, and `timeval_elapsed2()` provide timing helpers; `msleep()` sleeps with `select()`.

Control flow: shared memory setup creates `IPC_PRIVATE` memory, attaches it, immediately `IPC_RMID`s the id, zeroes the segment, and returns the attached pointer. `next_token()` either uses an explicit pointer or static continuation pointer, skips separators, copies until a separator outside quotes, and updates the caller pointer. Time helpers wrap `gettimeofday()`.

State and persistence behavior: SysV shared memory persists across forked children until all attachments exit, but is not left behind after process termination because the id is removed immediately. `next_token()` has static parser state when called with a null pointer. Other functions have no persistence.

Dependencies and integration: used by socket option parsing, child/rate timing, benchmark shared stats, and delay logic. Requires SysV shared memory APIs and standard POSIX time/select calls from `dbench.h`.

Risks: `all_string_sub()` assumes the destination buffer is large enough for expansions, so longer replacement strings can overflow caller storage. `next_token()` static state is not thread-safe and strips quotes rather than preserving escaped quotes. `shm_setup()` exits on allocation failure but returns NULL on attach failure after printing, creating inconsistent caller expectations.

Test signals: shared-memory smoke tests should fork and verify shared counters; token tests should cover comma/space separators and quoted tokens; substitution tests should include shrinking and expanding replacements with adequately sized buffers; timing tests should check monotonic-enough elapsed values for benchmark reporting.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/util.c -->
