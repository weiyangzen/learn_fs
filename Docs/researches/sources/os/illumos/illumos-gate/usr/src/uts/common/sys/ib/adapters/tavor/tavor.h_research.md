# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor.h

## Role

`tavor.h` is the umbrella driver header for the Tavor InfiniBand HCA driver. It includes the shared IBTF and Mellanox user-mapping ABI headers, pulls in all Tavor-specific subsystem headers, and defines the driver soft-state structure plus attach/detach, callback, device-mode, devmap, and user-resource database infrastructure.

## Major Definitions

The file defines VPD header sizes, initial soft-state count, minor-number instance encoding, PCI BAR indexes for CMD/UAR/DDR spaces, software-reset constants, attach-message helpers, and `TAVOR_WARNING()`.

IBTF callback macros enable, perform, and quiesce async/CQ callbacks using `ts_ibtfpriv` and `ts_in_evcallb`. Device-mode macros detect maintenance, compatibility, and HCA mode from PCI properties and distinguish operational modes.

`tavor_drv_cleanup_level_t` defines attach cleanup stages. `tavor_cmd_reg_t` records mapped HCR, ECR, clear-ECR, clear-interrupt, and software-reset register pointers plus the HCR lock.

`tavor_state_s` is the central per-instance state object. It stores device info, interrupt/MSI state, operational mode, GUIDs and HCA identity, IBTF registration data, BAR mappings and access handles, saved PCI config space, UAR resources, command registers, DDR/resource arenas, mailbox lists, outstanding command list, configuration profile, PD/EQ/CQ/QP/SRQ handle tables, QPN AVL tree, query-command snapshots, special-QP state, management-agent state, multicast shadow table, kstats, ioctl locks/flash state, PCI config handle, and fast-reboot quiesce state.

The user-mapping database structures define an AVL-protected database of mapped resources keyed by object/resource type/driver instance, plus optional on-close callbacks and devmap tracking reference counts.

## Interfaces

The file declares devmap handling, CI data input/output helpers, umap database initialization/finalization/allocation/free/add/find routines, user-memory unlock callback handling, and on-close callback registration/clearing/dispatch.

## Integration Notes

This header is the structural backbone of the Tavor driver. It ties attach/detach ordering, hardware register mapping, IBTF registration, resource management, ioctl flash access, and userland queue mapping into a single soft-state contract.
