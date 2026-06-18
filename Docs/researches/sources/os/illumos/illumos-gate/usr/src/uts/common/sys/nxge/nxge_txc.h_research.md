# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txc.h

## Purpose

`nxge_txc.h` defines the NXGE transmit-controller software state, statistics, error log, and public TXC entry points. TXC is the transmit-side controller that binds transmit DMA channels to ports and monitors reorder/store-forward error state.

## Main Definitions

`TXC_DMA_MAX_BURST_DEFAULT` is set to 1530 bytes, described as the hardware team's recommended DRR max burst.

`txc_errlog_t` contains reorder (`txc_ro_states_t`) and store-forward (`txc_sf_states_t`) state snapshots from `nxge_txc_hw.h`. `nxge_txc_stats_t` counts packets stuffed/transmitted, reorder and store-forward correctable/uncorrectable errors, address/DMA/length failures, packet assembly dead events, reorder errors, and the captured error log.

`nxge_txc_t` stores TXC configuration and current values: DMA max burst, DMA length, training vector, debug selector, control/status, port DMA bitmap/list, and a pointer to TXC stats.

## Interfaces

The exported functions initialize/uninitialize TXC, bind/unbind a TDC to TXC, handle TXC system errors, and inject TXC errors for debug/testing.

## Research Notes

This file is a thin software-facing wrapper around the much larger `nxge_txc_hw.h` register ABI. The interesting correctness boundary is TXDMA-to-port binding and error recovery: TXC state must agree with `nxge_txdma.h` rings and TXC hardware reorder/store-forward diagnostics.
