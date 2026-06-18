# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_zcp.h

## Purpose

`nxge_zcp.h` is the software-facing header for the NXGE zero-copy hardware block. It wraps the ZCP hardware definitions with statistics, error-log state, and initialization/recovery/debug entry points.

## Main Definitions

`zcp_errlog_t` stores a captured `zcp_state_machine_t` snapshot. `nxge_zcp_stats_t` tracks total errors and inits plus hardware-specific error counters: RRFIFO underrun/overrun, response FIFO uncorrectable error, buffer overflow, static/dynamic/buffer table parity errors, transfer-table programming and index errors, access failures, CFIFO ECC, and error log.

`nxge_zcp_t` stores ZCP config, interrupt config, and a pointer to stats.

## Interfaces

The exported functions initialize ZCP, inject ZCP errors, and perform fatal-error recovery.

## Research Notes

This is a compact software wrapper for `nxge_zcp_hw.h`. The important behavior lives in consumers that program ZCP tables and recover from ZCP fatal errors. Stats names map directly to interrupt/status bits in the hardware header.
