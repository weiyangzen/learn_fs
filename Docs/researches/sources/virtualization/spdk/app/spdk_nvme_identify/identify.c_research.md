# File Research: sources/virtualization/spdk/app/spdk_nvme_identify/identify.c

## Purpose
Implements `spdk_nvme_identify`, a comprehensive NVMe/NVMe-oF inspection utility. It discovers or connects to controllers, retrieves identify data, feature values, log pages, discovery records, OCSSD data, ZNS reports, FDP logs, and vendor-specific Intel logs, then prints decoded human-readable output.

## Main Entry Points
- `parse_args()` handles transport ID, hugepage/env settings, core selection, VMD, hex dump, socket backend, OCSSD verbosity, ZNS report limit, and log flags.
- `main()` initializes SPDK env, optionally initializes VMD, connects to a specific transport ID or probes controllers, prints controller data, detaches, and finalizes.
- `probe_cb()` applies host NQN to controller options.
- `attach_cb()` prints a discovered controller and queues async detach.
- `print_controller()` drives controller-level feature/log retrieval and prints controller, command set, log, health, power, ANA, discovery, vendor, and namespace data.
- `print_namespace()` prints active namespace metadata and dispatches OCSSD, ZNS, NVM, and FDP-specific detail paths.

## Internal Mechanics
The utility uses global buffers for log pages and a global `outstanding_commands` counter. Admin commands are submitted asynchronously but then drained by repeatedly calling `spdk_nvme_ctrlr_process_admin_completions()`.

Feature retrieval is serialized one feature at a time because some NVMe SSDs mishandle overlapping GET FEATURES commands. Controller features include arbitration, power management, temperature threshold, number of queues, and OCSSD media feedback. Namespace features include error recovery and FDP when supported.

Log collection includes error, health/SMART, firmware slot, ANA, command effects, discovery log, Intel SMART, Intel temperature, Intel marketing description, and FDP-specific logs. FDP configuration, reclaim unit usage, statistics, and events are fetched in header-then-full-buffer patterns when variable-sized.

ZNS handling prints ZNS namespace data and obtains zone reports through a temporary I/O qpair. OCSSD handling retrieves geometry and chunk information. NVM-specific data prints PI/storage-tag details.

The printer includes helpers for hex dumps, endian-safe field decoding, ASCII trimming, 128-bit counters, variable-width integers, opcode name mapping, CSI names, PI format names, and zone descriptor rendering.

## Dependencies
Depends on SPDK env, NVMe, NVMe-oF spec structures, NVMe ZNS, OCSSD, Intel NVMe extensions, VMD, socket backend selection, endian/string/util/UUID helpers, PCI IDs, and SPDK log flags.

## Filesystem/Block Relevance
This is a key diagnostic utility for NVMe-backed block storage. It exposes namespace size/capacity/utilization, LBA formats, metadata/PI format, deallocation/flush/write-zeroes/reservation support, ZNS geometry and zone state, FDP placement data, health counters, and discovery records for fabrics endpoints.

## Risks and Notes
- Many log buffers are dynamically allocated and freed in print paths; early exits can bypass cleanup.
- The tool exits on several command submission/allocation failures rather than attempting partial output.
- ZNS report count defaults to a limited number unless `-z` requests all zones or a specific limit.
- Discovery controllers skip most non-discovery log/feature retrieval.
- A specific `traddr` uses direct `spdk_nvme_connect()`; otherwise the tool probes matching controllers.
