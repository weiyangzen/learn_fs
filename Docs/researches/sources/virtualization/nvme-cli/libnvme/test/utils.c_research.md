# File Research: sources/virtualization/nvme-cli/libnvme/test/utils.c

This file provides shared test log-buffer utilities.

Functions:
- `test_setup_log()` creates a temporary file with `tmpfile()` and exits via `err(EXIT_FAILURE, ...)` on failure.
- `test_close_log(FILE *fd)` closes the log file.
- `test_print_log_buf(FILE *logfd)` prints buffered log output only if `ftell(logfd)` indicates content exists. It rewinds, copies data to stdout in 4096-byte chunks, prints begin/end sentinels, rewinds again, and truncates the temp file with `ftruncate()`.

Integration:
- Used by libnvme tests that want to capture noisy library logs and display them only after failure or at selected checkpoints.
- Depends on POSIX `fileno()`/`ftruncate()`.

Risk and maintenance notes:
- `ftell(logfd)` errors are not separately handled; a negative value would be treated as nonzero.
- `fwrite()` partial writes are handled in a loop, but a zero-length write breaks without surfacing an error.
