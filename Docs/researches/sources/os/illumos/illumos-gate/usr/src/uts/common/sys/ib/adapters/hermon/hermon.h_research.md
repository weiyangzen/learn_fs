# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon.h

## Role

`hermon.h` is the central private header for the Hermon InfiniBand HCA driver. It defines device constants, attach/reset helpers, state structures, DMA/ICM metadata, user mapping database structures, and prototypes for DMA, ICM, devmap, and user mapping management.

## Key Interfaces and Data

- Includes a large set of DDI, PCI, kstat, taskq, FMA, InfiniBand, Hermon command, configuration, resource, queue-pair, completion queue, event queue, memory registration, multicast, firmware, and agent headers.
- Defines initial attach state count, minor-number encoding, BAR identifiers for command/UAR/MSI-X regions, MSI-X maximum vectors, VPD sizing, PCI capability offsets, and software-reset constants.
- Diagnostic macros include warning emission, attach-message buffer helpers, and debug print masks.
- IBTF callback macros enable, invoke async/CQ callbacks, and quiesce callback execution with bounded polling.
- DDI property macros fetch vendor/device/revision IDs.
- Device modes distinguish maintenance and HCA operation; `HERMON_IS_OPERATIONAL()` checks mode.
- `hermon_dma_info_s` tracks DMA handle, access handle, kernel virtual address, ICM/device virtual address, allocation length, ICM reference count, DMA attributes, cookies, count, sync direction, access attributes, memory allocation flags, and callback.
- `hermon_cmd_reg_s` stores mapped command-register pointers such as interrupt clear, EQ arm, EQ CI set, software reset, semaphore, and firmware error buffer.
- `hermon_state_s` is the main per-instance state: identity, device mode, devinfo, PCI handles, attach state, ICM sizes, interrupt choices/priorities, EQ/CQ scheduling, HCA GUIDs, locks, UAR/blueflame mapping, software reset saved config, PCIe capability state, open state, command synchronization, resource handles, AVL trees/lists, kstats, hardware query/init structures, special QP state, agent task queues, firmware flash/log data, FMA state, MSI-X table/PBA mappings, and quiesce/fast reboot flags.
- Special QP resource masks identify QP0/QP1 resource allocation.
- User mapping database flags distinguish remove and ignore-instance searches.
- `hermon_umap_db_s`, private/common/entry/query structures track per-open mappings, key/value/type/instance pairs, callbacks on close, and lookup/query data.
- `hermon_devmap_track_s` records devmap offset and size.
- ICM constants split large tables; `hermon_bitmap()` and `hermon_index()` macros translate resource indexes through split bitmaps/tables.
- `hermon_icm_table_s` tracks ICM table busy state, base address, size, entry count, object size, span/split geometry, log sizes, bitmap array, DMA info array, and number-to-handle mapping.
- Prototypes cover DMA allocation/free/attribute initialization, ICM allocation/free/handle lookup, device mode, devmap handling, userland ioctl copyin/copyout, user mapping database init/fini/alloc/free/add/find callbacks, on-close callback management, and hardware resource-entry init/fini.

## Dependencies and Use

This is a driver-private integration header for Hermon source files. It depends on many other Hermon headers for resource types and hardware command structures. It is not a public InfiniBand consumer ABI.

## Research Notes

The file's most important asset is `hermon_state_t`, which centralizes nearly every driver subsystem: PCI mapping, interrupts, command handling, resource tables, ICM memory, firmware access, FMA, user mappings, and IBMF agents. It is a high-coupling private driver state contract.
