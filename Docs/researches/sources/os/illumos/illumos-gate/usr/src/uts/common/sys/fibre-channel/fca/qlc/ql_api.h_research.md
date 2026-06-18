# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_api.h

This is the central private API/state header for the QLogic `qlc` Solaris Fibre Channel adapter driver. It defines driver-wide constants, register access macros, queue state, DMA descriptors, target/LUN state, adapter state, flags, locking macros, return codes, and exported private function prototypes.

Key contents:
- Includes illumos SCSI, byteorder, PCI, DDI/FMA, QLogic open header, Fibre Channel public headers, and FCA interface definitions.
- Compatibility definitions and weak declarations for DDI interrupt APIs.
- PCIe/MSI/MSI-X/SR-IOV register constants and NPIV status fallback constants.
- Fibre Channel speed constants through 32Gbit.
- Bit constants `BIT_0` through `BIT_63`.
- DDI register access macros for normal registers, IO-mapped registers, and memory BAR registers.
- Fibre Channel constants for LUN limits, QLogic FCA brand, local ELS codes, loop IDs, fabric IDs, N-port handles, topology flags, timers, queue sizes, DMA attributes, and SG list limits.
- Register offset table `reg_off_t`, flash/NVRAM/VPD address maps for multiple adapter generations, flash error log constants, VPD tags, RISC-to-host status values, and HCCR commands.
- Initialization control blocks for older ISP adapters and 24xx+ adapters, including virtual-port configuration and extended initialization block support.
- IP initialization control blocks.
- DMA memory descriptor `dma_mem_t`, memory allocation/alignment enums, and 24-bit `port_id_t`.
- Intrusive link/list headers `ql_link_t` and `ql_head_t`.
- Request/response queue contexts `ql_request_q_t` and `ql_response_q_t`.
- Per-command state `ql_srb_t`, with transport packet, watchdog, unsolicited buffer, FCP, request sense, queue, IOCB, token, retry, and DMA SG context.
- SRB state flags for ISP started/completed, retry, poll, watchdog, ELS, unsolicited-buffer ownership/callbacks, FCP/IP/generic services, timeout, abort, device queue, token array, and management service.
- LUN and target queue structures:
  - `ql_lun_t` for per-LUN command queue, throttle, SCSI3 LUN address, and link.
  - `ql_tgt_t` for per-target locking, port ID, loop ID, outstanding count, IIDMA rate, watchdog, unsolicited-buffer state, retry counters, login state, port database data, PRLI data, and LUN queues.
- Target flags, IIDMA rates, kstat device/adapter stat structures, firmware code segment structure, dump state flags, extended logging trace structures, NVRAM cache descriptor, and PLOGI retry descriptor.
- Attach-progress flags and legacy interrupt-set structure.
- Mailbox data and LED state structures.
- `ql_adapter_state_t`, the central adapter object with:
  - global HBA linkage, locks, state flags, topology, timers, BB_CR state;
  - task daemon and completion taskq state;
  - interrupt handles and capabilities;
  - outstanding command tokens;
  - request/response queues;
  - receive buffer queue;
  - mailbox synchronization;
  - unsolicited buffer tracking;
  - device queues and kstats;
  - PCI and device mappings;
  - Solaris FCA registration data;
  - firmware, RISC, NVRAM, power-management, SBus, ioctl, cache, dump, trace, virtual-port, FCoE, NetXen, DMA attribute, and FMA state.
- Adapter state flags, task daemon flags, mailbox flags, configuration flags, interrupt flags, endian helpers, loop/device validity macros, daemon/loop readiness macros, interrupt-pending macro, and locking macros.
- Local return/status codes, SBus FPGA definitions, port ID/name extraction macros, ELS command table initializer, ELS descriptor structures, PRLI response structures, globals, and many private function prototypes for flash, firmware dump, DMA, queues, ELS, device lookup, loop state, unsolicited buffers, NVRAM cache, PLOGI params, interrupts, and module dump templates.

Dependencies:
- Depends on many qlc-specific types from other headers, including `ql_adapter_revlvl_t` from `ql_apps.h` and firmware/NVRAM types from `ql_init.h`.
- Uses illumos Fibre Channel types such as `fc_packet_t`, `fc_unsol_buf_t`, `fc_fca_tran_t`, `fca_port_attrs_t`, `la_els_logi_t`, `fcp_cmd_t`, and `la_wwn_t`.

Research notes:
- `ql_adapter_state_t` is the main driver architecture map; most qlc source files operate on it.
- The header preserves compatibility across many QLogic adapter generations: 22xx/23xx/24xx/25xx/27xx/80xx/81xx/82xx/83xx, FC and FCoE.
- Filesystem relevance is through storage I/O: this is a Fibre Channel HBA driver surface used by SCSI/FCP storage paths.
