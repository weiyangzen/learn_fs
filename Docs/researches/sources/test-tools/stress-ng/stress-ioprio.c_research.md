# sources/test-tools/stress-ng/stress-ioprio.c

Purpose: implements `ioprio`, a Linux I/O-priority stressor that rapidly queries and changes process I/O priority classes while issuing vectored writes and syncs to a temporary file.

Important APIs/types/functions: the file relies on `core-io-priority.h` wrappers `shim_ioprio_get()` and `shim_ioprio_set()`, Linux `IOPRIO_WHO_*` selectors, `IOPRIO_PRIO_VALUE()`, and `pwritev()`. Constants set a small four-iovec write size and bounded temp-file footprint.

Control flow: `stress_ioprio()` creates an unlinked temp file, reports expected disk usage, sync-starts, then loops through process, process-group, and user `ioprio_get` calls. It exercises invalid selectors and IDs, fills four small buffers, writes randomly within a fixed range, fsyncs, attempts invalid `ioprio_set` calls, then applies idle, best-effort priorities 0-7, and realtime priorities 0-7 around more writes and fsyncs.

State and persistence behavior: file data is temporary and unlinked; the main side effect is repeated mutation of the current process I/O priority. The priority is not explicitly restored, so process teardown is relied on for cleanup.

Dependencies and integration points: compiled only when `ioprio_get`, `ioprio_set`, and `pwritev` are available. Uses stress-ng temp directory, settings, sync, random, and filesystem usage helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS` with always-on verification.

Risks: realtime I/O priority may require privilege; the code tolerates `EPERM` and `EINVAL` but treats other errors as failures. Filesystems can return `ENOSPC` on `pwritev`, which is accepted. Behavior varies by scheduler and kernel configuration.

Test signals: run with and without privilege, verify no unexpected ioprio errors, temp directory cleanup, and bogo progress under `--verify`. Check that `ENOSPC`, `EPERM`, and unsupported priority classes are handled as expected.
