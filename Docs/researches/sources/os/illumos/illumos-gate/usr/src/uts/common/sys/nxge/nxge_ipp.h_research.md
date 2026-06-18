# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_ipp.h

## Purpose
Defines IPP software state, statistics, error log structures, limits, and lifecycle/error-handling prototypes for the IP Packet Processing block.

## Main Interfaces
- Limits:
  - `IPP_MAX_PKT_SIZE`
  - `IPP_MAX_ERR_SHOW`
- `ipp_errlog_t`: multiple-error flag, DFIFO read pointer, state machine, and ECC syndrome.
- `nxge_ipp_stats_t`: counters for init/error events, missed SOP/EOP, DFIFO ECC, PFIFO parity/over/underflow, checksum errors, packet discard, and saved errlog.
- `nxge_ipp_t`: configuration, interrupt config, status register snapshot, max packet size, and stats pointer.
- Prototypes:
  - `nxge_ipp_reset()`
  - `nxge_ipp_init()`
  - `nxge_ipp_disable()`
  - `nxge_ipp_drain()`
  - `nxge_ipp_handle_sys_errors()`
  - `nxge_ipp_fatal_err_recover()`
  - `nxge_ipp_eccue_valid_check()`
  - `nxge_ipp_inject_err()`

## Dependencies And Relationships
Includes `nxge_ipp_hw.h` and `npi_ipp.h`. IPP state is embedded in higher-level driver state and initialized through routines declared in `nxge_impl.h`.

## Research Notes
This header is the software-facing wrapper around the IPP hardware register definitions. Error handling is a first-class part of the interface.
