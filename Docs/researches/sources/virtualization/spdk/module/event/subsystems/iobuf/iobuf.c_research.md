# File Research: sources/virtualization/spdk/module/event/subsystems/iobuf/iobuf.c

Registers SPDK iobuf as an event subsystem and writes iobuf config JSON.

Key elements:
- Initializes via `spdk_iobuf_initialize()`.
- Finishes asynchronously via `spdk_iobuf_finish()`.
- Writes `iobuf_set_options` config with small/large pool counts, buffer sizes, and NUMA option.
- Registers subsystem name `iobuf`.

Dependencies:
- Uses SPDK iobuf, bdev, thread, init, and JSON APIs.

Research notes:
- This subsystem has no declared dependencies but is a dependency for accel, bdev, nvmf, and ublk.
