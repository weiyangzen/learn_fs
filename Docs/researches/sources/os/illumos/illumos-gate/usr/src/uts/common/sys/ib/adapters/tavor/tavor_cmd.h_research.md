# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_cmd.h

## Role

`tavor_cmd.h` defines the Tavor firmware command interface. It names firmware opcodes and completion statuses, describes mailbox and outstanding-command pools, defines command-post payloads, handles MAD endianness conversion helpers, and declares the command wrappers used by the rest of the driver.

## Major Definitions

The header defines command polling defaults, mailbox counts/sizes/alignment, and `TAVOR_MBOX_IS_SYNC_REQ()` for deciding whether mailbox DMA sync is required.

Firmware opcodes cover system enable/disable, device/firmware/DDR/adapter/HCA queries, HCA and IB port init/close/set operations, MPT/MTT/TPT operations, EQ/CQ/QP/SRQ ownership and state transitions, MAD interface, multicast table operations, debug, diagnostics, static config modification, and MPT modification. Status constants include hardware statuses plus driver-defined insufficient-resource, timeout, and invalid-status values.

QP command flags cover special QP type, QP transition opmasks, SQD event requests, direct-to-reset behavior, output-mailbox modifiers, SYS_EN modes, MAP_EQ mapping/unmapping, and MAD_IFC modes/sizes/attributes. Endian-aware macros convert common SM MAD responses for PortInfo, NodeInfo, GUIDInfo, and PKeyTable.

`tavor_mbox_t`, `tavor_mboxlist_t`, and `tavor_mbox_info_t` implement fast mailbox allocation/free pools. `tavor_cmd_t` and `tavor_cmdlist_t` similarly manage outstanding firmware command slots. `tavor_cmd_post_t` mirrors HCR command fields plus command flags.

## Interfaces

The file declares generic command posting, mailbox allocation/free, command completion handling, mailbox list initialization/finalization, outstanding-command list management, and wrappers for SYS_EN/DIS, INIT/CLOSE HCA, INIT/CLOSE/SET IB, QP transitions, queries, ownership transitions, MAD_IFC helpers, WRITE_MTT, SYNC_TPT, MAP_EQ, RESIZE_CQ, special-QP configuration, multicast commands, MOD_STAT_CFG, and MODIFY_MPT.

## Integration Notes

This is the Tavor control-plane API to firmware. It coordinates with event handling when commands complete through EQs and with resource code when mailbox allocation must obey sleep/non-sleep context rules.
