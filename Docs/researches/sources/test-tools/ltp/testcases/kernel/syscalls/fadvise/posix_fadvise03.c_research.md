# sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise03.c

Purpose: Checks `posix_fadvise()` returns `EINVAL` for advice values outside the architecture-defined set.

Important APIs/types/functions: `ADVISE_LIMIT`, `is_defined_advise()`, `posix_fadvise`, `lapi/abisize.h`, and special 31-bit s390 handling for `DONTNEED`/`NOREUSE` values.

Control flow: `setup()` opens `/bin/cat`; test indexes from 0 to 31 skip values recognized as defined and call `posix_fadvise` on the rest, expecting `EINVAL`.

State and persistence behavior: Only the open fd is persistent test state. Architecture-specific defined values are encoded in the `defined_advise` array.

Dependencies and integration points: The file integrates syscall API behavior with ABI-specific constants.

Risks and test signals: Risk is architecture drift: if new advice values are added under 32, this test needs updating to avoid false failures.
