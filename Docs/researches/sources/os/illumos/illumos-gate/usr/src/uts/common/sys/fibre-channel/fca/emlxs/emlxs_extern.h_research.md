# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_extern.h

Purpose: Central external declaration hub for the `emlxs` driver. It exposes global driver state, device/DMA attributes, configuration tables, firmware/model tables, SLI APIs, and cross-module function prototypes.

Key declarations:
- Driver globals: `emlxs_soft_state`, `emlxs_instance`, `emlxs_instance_count`, revision/version/name/label strings, and `emlxs_device`.
- DDI/DMA globals: access attributes and DMA attribute variants.
- Message/logging APIs: message formatting, log create/destroy/reinit/get.
- Event APIs: event queue lifecycle, link/RSCN/CT/dump/temp/FCoE/async logging, DFC event retrieval, optional SAN diagnostic event logging.
- Solaris FCA integration: link up/down callbacks, ULP callbacks, packet init/uninit/transport/abort, unsolicited buffer handling, reset and port management.
- Utility APIs: WWN formatting/compare, command translators, byte swapping, mode translation, power-management helpers, VPD/FCode parsing.
- Optional feature sections: `DHCHAP_SUPPORT`, `MENLO_SUPPORT`, `FMA_SUPPORT`, `MODFW_SUPPORT`, `MSI_SUPPORT`, `SFCT_SUPPORT`, `DUMP_SUPPORT`.
- Mailbox APIs: SLI2/3/4 mailbox construction, queue create commands, FCF/VFI registration, FCF table reads, async event handling, completion and retry helpers.
- Memory APIs: pool creation/destruction/get/put, buffer allocation, HBQ allocation, virtual-address lookup.
- HBA and SLI APIs: adapter init, firmware decode/show/load/unload, interrupt setup, SLI3/SLI4 object mapping and reset helpers.
- FCP path APIs: packet registration, abort/close IOCB creation, chip/transmit queue operations, link/online/offline transitions, buffer posting.
- Thread/task APIs: taskq lifecycle, worker thread lifecycle, thread triggers, spawn thread management.
- DFC, dump, FCT, FCF, VPI, and RPI notification APIs.

Dependencies and interactions:
- This file assumes all core driver types have already been declared: `emlxs_hba_t`, `emlxs_port_t`, `MAILBOXQ`, `IOCBQ`, `CHANNEL`, `NODELIST`, `MATCHMAP`, `FCFIobj_t`, `VFIobj_t`, `XRIobj_t`, `RPIobj_t`, and others.
- It is the cross-module compile contract for implementation files such as `emlxs_msg.c`, `emlxs_event.c`, `emlxs_solaris.c`, `emlxs_pkt.c`, `emlxs_mbox.c`, `emlxs_mem.c`, `emlxs_hba.c`, `emlxs_sli3.c`, `emlxs_sli4.c`, `emlxs_diag.c`, `emlxs_download.c`, `emlxs_fcp.c`, `emlxs_thread.c`, `emlxs_dfc.c`, `emlxs_dump.c`, and `emlxs_fcf.c`.

Implementation notes:
- This header is declarations only, but it strongly documents driver modular boundaries.
- Several feature areas are compile-time optional, so call sites must honor matching feature guards.
- It includes duplicate declarations for `emlxs_instance` and `emlxs_instance_count`; changing that would be cleanup, not behavior.
