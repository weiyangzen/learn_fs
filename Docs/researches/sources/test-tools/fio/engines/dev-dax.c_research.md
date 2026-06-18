# sources/test-tools/fio/engines/dev-dax.c

Purpose: Implements a synchronous `dev-dax` engine that reads and writes device DAX character devices through mmap and persistent memory copies.

Important APIs/functions: Registers `dev-dax` with init, prep, queue, open/close, and get-file-size callbacks. Internal helpers map full or limited regions: `fio_devdax_file()`, `fio_devdax_prep_full()`, `fio_devdax_prep_limited()`, and `fio_devdax_prep()`.

Control flow: Open delegates to `generic_open_file()` and allocates per-file `fio_devdax_data`. File size discovery validates character device type, checks sysfs subsystem is `dax`, reads `/sys/dev/char/MAJ:MIN/size`, and stores size. Prep reuses an existing mapping if the IO falls inside it; otherwise it unmaps, attempts a full-file mapping unless partial mode is set or size overflows, then falls back to a limited mapping capped at 1 GiB. Queue performs `memcpy()` for reads and `pmem_memcpy_persist()` for writes; sync-like directions complete as no-ops.

State/persistence: Per-file engine data stores mapping pointer, mapped size, and offset. Partial mmap state is tracked in fio file flags.

Dependencies/integration: Requires libpmem, mmap, sysfs char device metadata, fio verify flags, and generic file open/close.

Risks: Pointer arithmetic on `void *` relies on compiler extension. `fio_devdax_get_file_size()` logs a non-DAX device but does not immediately return after the basename mismatch. Mapping alignment and block-size constraints depend on device/page size. Close frees mapping metadata but does not explicitly unmap an active mapping in this file.

Test signals: Exercise DAX device detection, full and limited mapping fallback, read/write persistence, offset bounds, verify-enabled write protections, and cleanup with changing mappings.
