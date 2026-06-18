# sources/test-tools/fio/zbd.h

Purpose: public ZBD interface and main in-memory zone/device state definitions.

Important APIs/types: `enum io_u_action` communicates accept/eof/completed decisions. `struct fio_zone_info` stores per-zone mutex, start, write pointer, capacity, inflight/error counters, type, condition, and flags (`has_wp`, `write`, `reset_zone`, `fixing_zone_wp`). `struct zoned_block_device_info` stores model, max write/active zones, mutex, zone size/log2, valid data bytes, write range, zone count, refcount, write target array, and flexible zone array. Function declarations expose setup, close, IO adjustment, trim, stats, error logging, and recovery.

Control flow/state: inline `zbd_close_file()` frees shared zone info. `zbd_queue_io_u()` and `zbd_put_io_u()` dispatch per-`io_u` callbacks set by `zbd_adjust_block()` and clear callback pointers afterward.

Dependencies/integration: includes fio `io_u`, ioengine, block-zoned abstraction, and `zbd_types.h`.

Risks/test signals: struct fields are mutated under specific locks documented mostly in `zbd.c`; callers must not bypass callback cleanup. Header tests should compile users with and without zoned IO engines and validate flexible-array sizing assumptions.
