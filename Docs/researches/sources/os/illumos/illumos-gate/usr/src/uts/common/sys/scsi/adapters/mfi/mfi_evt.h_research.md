# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_evt.h

## Role

MFI event and asynchronous event notification definition header.

## Key Elements

- Forward-declares AEN, event log, event detail/list, and all event argument structures.
- Defines event codes for configuration, patrol-read, logical-drive initialization/check/creation/deletion/state, physical-drive insertion/removal/change/reset/progress, foreign configuration, controller property/performance/boot/personality changes, and snapdump count.
- Defines event classes from debug/progress/info through fatal/dead.
- Defines event locales for logical drive, physical drive, enclosure, BBU, SAS, controller, config, cluster, and all.
- Defines event argument type IDs for none, CDB/sense, logical drive, physical drive, counts, LBAs, owners, progress, state, PCI, rate, string, time, and ECC.
- Packed structures:
  `mfi_aen_t`, `mfi_evt_t`, `mfi_evt_log_info_t`, logical/physical drive argument variants, CDB/sense payload, PCI/time/ECC arguments, and `mfi_evt_detail_t`.
- `mfi_evt_detail_t` stores sequence, timestamp, code, class/locale, argument type, a union of typed arguments or string, and a description string.
- `mfi_evt_list_t` is a variable-length event-list wrapper.

## Dependencies and Coupling

Includes `mfi.h` for common types such as `mfi_progress_t`. Size of `mfi_evt_detail_t` is asserted to 256 bytes.

## Research Notes

The event format is designed for firmware log retrieval and AEN processing. The typed union makes event interpretation depend on `evt_argtype`.
