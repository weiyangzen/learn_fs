# sources/test-tools/fio/zbd_types.h

Purpose: standalone ZBD type and constant definitions shared by fio ZBD code and lower-level zoned abstractions.

Important APIs/types: `ZBD_MAX_WRITE_ZONES` caps tracked write target zones at 4096. `enum zbd_zoned_model` defines none, host-aware, and host-managed models. `enum zbd_zone_type` defines conventional, sequential-write-required, sequential-write-preferred, and sequential-before-required values. `enum zbd_zone_cond` mirrors zone conditions such as empty, implicit/explicit open, closed, read-only, full, and offline. `struct zbd_zone` is a zone-report descriptor with start, write pointer, length, capacity, type, and condition.

Control flow/state: no executable logic; used as ABI-like shared definitions.

Dependencies/integration: includes `<inttypes.h>`. Consumed by `zbd.c`, `zbd.h`, and `oslib/blkzoned` adapters.

Risks/test signals: enum values must match kernel/ioengine reports. Any change risks misinterpreting zone conditions. Compile-time tests should verify expected numeric constants when adapting to new platforms.
