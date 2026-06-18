# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_hw.h

## Role

`tavor_hw.h` is the hardware ABI definition header for the Tavor HCA. It maps command BAR offsets, firmware mailbox layouts, resource-context entries, event/completion entries, queue-pair contexts, doorbells, WQE segments, undocumented register offsets, and flash-interface constants.

## Major Definitions

The header defines CMD BAR offsets for HCR, ECR, clear-ECR, clear-interrupt, and software reset registers; hardware/software ownership constants; and address-translation enablement constants.

Firmware command layouts include:
- `tavor_hw_hcr_s` and masks/shifts for command status, go bit, event bit, opmod, opcode, and token.
- `QUERY_DEV_LIM`, `QUERY_FW`, `QUERY_DDR`, and `QUERY_ADAPTER` result structures and revision/version constants.
- `INIT_HCA`/`QUERY_HCA` component structures for QP/EQ/CQ/RDB context bases, UDAV memory, multicast, TPT, UAR, and full HCA setup.
- `INIT_IB` port setup fields.

Memory and queue resource layouts include MPT, MTT, EQC/EQE, CQC/CQE, SRQC, MOD_STAT_CFG, UDAV, QP address paths, QPC entries, MCG entries, and performance counters. Most major firmware structures have separate little-endian and big-endian bitfield definitions.

Doorbell and work-queue definitions cover UAR send/receive/CQ/EQ doorbells, send WQE segments, MLX special-QP WQEs, receive WQE segments, SGL entries, and many macros for building WQEs with explicit DDI 32/64-bit writes.

The final sections define undocumented port/stat/GID/PKey register offsets and macros, plus flash PCI/config/register offsets, masks, timeouts, and Intel flash command-set constants.

## Interfaces

There are no C function prototypes. The file exports structures and macros consumed by command, CQ, EQ, QP, MR, multicast, ioctl, flash, and work-request code.

## Integration Notes

This is highly layout-sensitive firmware/hardware contract code. Field order, bit positions, endian variants, owner bits, and DDI accessor usage must match Tavor hardware expectations. Several fast-path WQE builders intentionally avoid C bitfield stores to reduce read-modify-write behavior.
