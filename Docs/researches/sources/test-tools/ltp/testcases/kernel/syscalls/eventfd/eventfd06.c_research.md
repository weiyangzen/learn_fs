# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd06.c

Purpose: Exercises eventfd overflow notification through Linux AIO, where kernel-space completion increments can overflow a saturated eventfd counter.

Important APIs/types/functions: `libaio` APIs `io_setup`, `io_prep_pwrite`, `io_set_eventfd`, `io_submit`, `io_getevents`, `poll()`, `select()`, `eventfd`, `SAFE_OPEN`, and feature guards `HAVE_LIBAIO`/`HAVE_IO_SET_EVENTFD`.

Control flow: `setup()` initializes an AIO context, opens a temp file, and creates a nonblocking eventfd. Each subtest clears any pending counter, writes `UINT64_MAX - 1`, submits one async pwrite tied to the eventfd, then checks overflow state through `select()` or `poll()` and finally reads `UINT64_MAX`.

State and persistence behavior: Persistent state is limited to a temporary file used for AIO writes. Kernel state includes the AIO context, eventfd counter, and readiness/error flags produced by overflow.

Dependencies and integration points: Requires libaio, AIO eventfd support, a tmpdir, and `CONFIG_EVENTFD`. Unsupported kernels or build configurations return `TCONF` rather than false failures.

Risks and test signals: Overflow can only be reached by kernel-side increments, so the AIO path is essential. The select subtest currently uses the regular file descriptor in the fdset while reading `evfd` for the counter; that makes this source worth reviewing if the intended readiness check is specifically the eventfd descriptor. Poll explicitly checks `POLLERR` on `evfd`.
