# sources/test-tools/fio/engines/xnvme.c

## Purpose
`xnvme.c` implements fio's `xnvme` ioengine using the xNVMe C API for NVMe devices, including backend selection, asynchronous queues, vectored I/O, metadata/protection information handling, zoned namespace operations, and FDP RUH fetching.

## Important APIs, Types, And Functions
`struct xnvme_fioe_fwrap` wraps each fio file with an xNVMe device, geometry, queue, LBA/metadata sizing, and fio file pointer. `struct xnvme_fioe_data` stores the completion queue, completion/error counters, round-robin file indexes, open/allocation counts, optional iovec arrays, and flexible file wrappers. `struct xnvme_fioe_request` stores per-I/O PI context and metadata buffer. Options select xNVMe backend/memory/async/sync/admin interfaces, namespace ID, subnqn, iovec mode, metadata size, and PI checks/tags.

Core paths include `xnvme_opts_from_fioe()`, `_dev_open()`, `_verify_options()`, `xnvme_fioe_init()`, xNVMe buffer allocation/free hooks, per-`io_u` init/free, `xnvme_fioe_queue()`, `cb_pool()`, `xnvme_fioe_getevents()`, and ZBD/FDP helpers.

## Control Flow
`.init` requires `--thread=1`, allocates `xnvme_fioe_data`, completion/iovec arrays, and opens every fio file under a global mutex because xNVMe setup is serialized. `_dev_open()` opens the device, initializes an async queue, captures geometry, adjusts LBA/metadata sizes for PI action, validates fio block sizes/verify compatibility, and marks file size known. `.queue` computes SLBA/NLB, gets an xNVMe command context, populates NVMe read/write command fields, optionally generates PI metadata for writes, uses scalar or vectored `xnvme_cmd_pass*`, and returns queued/busy/completed. `cb_pool()` verifies completions and PI on reads, appends `io_u` to `iocq`, and releases the context. `.getevents` round-robins device queues with `xnvme_queue_poke()` until `min` completions are available.

## State And Persistence
Device handles and queues are per thread but protected during open/close and pre-init helper operations by `g_serialize`. Data persists on NVMe targets. Metadata buffers are allocated per `io_u` when requested. Zoned helper calls sometimes open temporary devices before engine initialization and sometimes reuse initialized wrappers.

## Dependencies And Integration Points
Dependencies include `libxnvme`, fio verify, ZBD types, data placement/FDP types, pthreads, and fio raw/diskless/memalign flags. The engine registers `xnvme` with hooks for memory allocation, eventing, file size, ZBD model/report/reset, max open zones, and FDP RUHS.

## Risks
Several error paths assert false after runtime I/O failures, which is harsh for production benchmarking. `_dev_close()` calls `xnvme_queue_term()` when `dev` is set but does not separately check `queue`. `_dev_open()` compares `f->fileno > nallocated` rather than `>=`, which should be reviewed. `getevents` can spin indefinitely if completions never arrive and timeout is ignored. PI/metadata validation is complex and tied to geometry; block-size and verify combinations need careful testing.

## Test Signals
Tests should cover backend option construction, block-size validation, PI action/check combinations, vectored and non-vectored I/O, metadata buffers, busy queue handling, multi-file queue polling, zoned model/report/reset conversion, max-open-zone overflow behavior, FDP RUH fetch, and cleanup after partial init failure. Real validation requires xNVMe-capable devices or emulation.
