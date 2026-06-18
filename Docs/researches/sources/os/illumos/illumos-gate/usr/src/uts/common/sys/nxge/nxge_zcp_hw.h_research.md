# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_zcp_hw.h

## Purpose

`nxge_zcp_hw.h` defines the Neptune zero-copy hardware ABI. It describes ZCP configuration/status/mask registers, buffer-address-map and destination-region controls, RAM access/data registers, CFIFO reset/ECC state, transfer table entry formats, RAM selectors, training/state-machine registers, packet zero-copy header state, and ECC injection control.

## Configuration And Interrupts

The top-level registers include config, interrupt status, interrupt test, interrupt mask, BAM region controls for 4/8/16/32 buffer regions, DST region controls for matching sizes, RAM data and byte-enable/access registers, training vector, state machine, check-bit data, CFIFO reset, and per-port CFIFO ECC registers.

`zcp_config_reg_t` exposes 32-bit mode, debug selector, RDMA threshold, ECC/parity check disable, buffer request disables, and zero-copy enable. `zcp_int_stat_reg_t` / mask layout covers RRFIFO underrun/overrun, response FIFO uncorrectable error, buffer overflow, static/dynamic/buffer table parity, transfer-table program/index errors, and CFIFO ECC for ports 0 through 3.

## BAM/DST And Transfer Table Entries

`zcp_bam_region_reg_t` defines logical offset, first/last zero-copy flow IDs, range-check enable, and LOJ. `zcp_dst_region_reg_t` defines destination offset.

`tte_sflow_attr_t` is the static flow table entry with five quadwords containing RDC table offset, buffer size/count, ULP end, ring base/size, skip, transfer mode, unmap controls, busy, TOQ, and data nibble fields. `tte_dflow_attr_t` is the dynamic flow entry with mapped-in state, anchor sequence, anchor buffer/offset flags, ULP-end/unmap status, error status, write pointer, head-of-queue, prefetch flag, and data nibble.

Enums define transfer buffer sizes from 4K through 8M, buffer counts 4/8/16/32, transfer modes basic/auto-unmap/auto-advance, and transfer ring sizes from 8 through 32K.

## RAM Access And Packet State

`zcp_ram_access_t` selects read/write, ZCFID, RAM selector, and CFIFO. RAM selectors cover eight BAM banks, static/dynamic transfer tables, and four CFIFOs. `zcp_ram_benable_t` provides byte enables. `zcp_ram_data_t` overlays static and dynamic table entries.

`zcp_hdr_t` is a software header describing a zero-copy flow packet: flow ID, TCP header/payload length, head of queue, first buffer offset, end-of-buffer reach flag, DMA window crossing type, and window buffer offset. `zcp_state_machine_t` and `zcp_training_vector_t` expose diagnostic state. `zcp_ecc_ctrl_t` controls ECC error injection/correction selection.

## Research Notes

ZCP is table-driven and stateful; mistakes in transfer table bitfields can cause DMA into the wrong buffer or failed auto-unmap behavior. Audit-sensitive areas are RAM access busy/read-write sequencing, byte-enable masks, BAM/DST range checks, ULP-end/unmap flags, and CFIFO reset/ECC handling.
