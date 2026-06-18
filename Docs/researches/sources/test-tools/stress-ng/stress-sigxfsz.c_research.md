# sources/test-tools/stress-ng/stress-sigxfsz.c

Purpose: implements the `sigxfsz` stressor, repeatedly setting low file-size limits and writing past them to generate EFBIG and SIGXFSZ.

Important APIs/types/functions: `stress_sigxfsz_handler`, `stress_sigxfsz`, `getrlimit`, `setrlimit`, `RLIMIT_FSIZE`, `SIGXFSZ`, `pwrite` or `lseek` plus `write`, temp-file helpers, and metrics export.

Control flow: the worker installs SIGXFSZ handler, reads current file-size limit, creates an unlinked temp file, synchronizes start, then each iteration chooses a random soft file-size limit, sets it, writes four bytes at that limit with `pwrite` or seek/write, increments bogo ops on EFBIG, and shrinks the random maximum if `setrlimit` returns EINVAL. It records SIGXFSZ signals/sec, ignores SIGXFSZ on exit, closes the fd, and removes the temp directory.

State and persistence behavior: state is process `RLIMIT_FSIZE`, an unlinked temp file, and volatile async signal count. The file is not durable after close.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify, and unimplemented without SIGXFSZ or `RLIMIT_FSIZE`. It uses stress-ng temp filesystem helpers and optional `pwrite`.

Risks and test signals: resource-limit behavior varies under shells/containers. Risks include not restoring the original file-size limit in-process, repeated EINVAL reducing test range too far, missing SIGXFSZ despite EFBIG, or temp fd cleanup errors.
