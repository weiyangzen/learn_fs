# File Research: sources/virtualization/spdk/app/fio/nvme/fio_plugin.c

## Purpose
Implements fio's `spdk` ioengine for direct SPDK NVMe access. It parses fio file names as NVMe transport IDs, connects to controllers/namespaces, allocates I/O qpairs, and submits NVMe commands directly.

## Main Entry Points
- `spdk_fio_setup()` initializes SPDK env once, optionally initializes VMD/tracing, parses per-file transport IDs, probes/connects controllers, and discovers namespaces.
- `probe_cb()` applies host NQN, WRR, interrupt, and digest options to controller options.
- `attach_cb()` registers or reuses controllers, resolves namespace IDs, validates block sizes, configures PI and ZNS settings, and sets fio file size/type.
- `spdk_fio_open()` allocates an NVMe I/O qpair for a fio file.
- `spdk_fio_queue()` maps fio read/write/trim to NVMe read/write, SGL read/write, zone append, or dataset management commands.
- `spdk_fio_getevents()` round-robins qpairs and processes completions.
- ZNS callbacks implement fio zoned model, zone reporting, reset write pointer, and max-open-zone queries.
- FDP support exposes `fdp_fetch_ruhs()` for compatible fio versions.

## Internal Mechanics
Global controller state is shared under `g_mutex`, while each fio thread owns a list of `spdk_fio_qpair` objects and a completion queue. A separate pthread periodically processes admin completions for all connected controllers.

The plugin supports PCIe and NVMe-oF transport IDs. If a namespace is not specified, it uses the first active namespace. For PCIe addresses, it normalizes the PCI address string. For fabrics, it can derive or override host NQN.

I/O can use contiguous buffers or fio-provided SGL callbacks. The SGL path supports splitting by configured SGE size and optionally using bit bucket descriptors for read data. Trim maps to NVMe dataset management, with multi-range trim support when fio exposes it.

Protection information support configures NVMe PI flags, builds SPDK DIF/DIX contexts, generates PI for writes, verifies PI on reads, and supports both extended LBA and separate metadata modes.

ZNS support detects ZNS command-set namespaces, optionally resets all zones at initialization, maps fio zone reports from NVMe ZNS reports, and optionally converts writes to zone append.

## Options
Includes WRR, interrupt mode, queue priority/weights, memory size, shared memory ID, SGL settings, bit bucket length, host NQN, PI action/check settings, metadata buffer sizing, TCP digest settings, VMD enablement, initial zone reset, zone append, qid mapping print, tracing, log flags, and PCIe SGL merge control.

## Dependencies
Depends on SPDK NVMe, NVMe ZNS, VMD, env, DIF/DIX, tracing, endian/string/util helpers, and fio version-specific APIs for ZBD, FDP, and multi-range trim.

## Filesystem/Block Relevance
This plugin benchmarks raw NVMe hardware and NVMe-oF paths without the bdev layer, exposing controller, namespace, queue, metadata, and zoned behavior directly to fio.

## Risks and Notes
- Requires fio `thread=1`.
- Global plugin configuration is established by the first initialization path and shared across jobs.
- Admin completion polling is done by a cancellable pthread.
- PI buffer sizing must cover metadata needs; the code caps per-I/O metadata to configured allocation.
- ZNS report/reset paths allocate temporary qpairs before normal fio open.
- FDP directives require SGL writes.
