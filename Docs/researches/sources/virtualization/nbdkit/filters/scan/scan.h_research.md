# File Research: sources/virtualization/nbdkit/filters/scan/scan.h

This header defines the shared interface between the scan filter front-end and its background worker. It exports the global scan parameters `scan_clock`, `scan_forever`, and `scan_size`, which are configured in `scan.c` and consumed by the worker implementation outside this file.

The central data structures are `struct command`, with `CMD_QUIT` and `CMD_NOTIFY_PREAD` variants plus an offset, and `struct bgthread_ctrl`, which holds the command vector, mutex, and `nbdkit_next *` used to issue cache operations. `DEFINE_VECTOR_TYPE(command_queue, struct command)` provides the generated vector API used by `scan.c`.

The public worker entry point is `scan_thread(void *)`. Correctness depends on all producers and the worker respecting `bgthread_ctrl.lock` for command queue access and on `scan_size` staying validated by `scan_config_complete`.
