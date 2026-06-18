# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_pd.h

## Role

MFI physical-drive definition header.

## Key Elements

- Defines physical-drive firmware states: unconfigured good/bad, hot spare, offline, failed, rebuild, online, copyback, and system.
- Defines physical-drive cache policy values.
- `mfi_pd_ref_t` identifies a physical drive by device ID and sequence number.
- `mfi_pd_info_t` is a 512-byte packed physical-drive information block containing:
  inquiry and VPD data, device type, connected ports, speed, media/other/predictive error counts, firmware state, removal/link state, DDF type flags, path information and SAS addresses, raw/non-coerced/coerced sizes, enclosure/slot info, rebuild/patrol/clear/copyback/erase/locate progress, bad-block and config usability flags, extended VPD, power/enclosure position, allowed operations, copyback/enclosure partners, security state, media and bridge identity, SAT bridge flag, interface/temperature/blocksize fields, PI/NCQ/WCE/UNMAP properties, shield diagnostic state, alternate link speed, BBM error count, and reserved padding.
- `mfi_pd_cfg_t` maps firmware physical-drive sequence/device handle to target ID and task-management capability.
- `mfi_pd_map_t` is a variable-length physical-drive config map.
- `mfi_pd_addr_t` describes physical-drive address/location and SAS addresses.
- `mfi_pd_list_t` is a variable-length physical-drive address list.

## Dependencies and Coupling

Includes `mfi.h` for shared progress and MFI types. The size assertion for `mfi_pd_info_t` is skipped under `__CHECKER__` due to a known smatch packing issue.

## Research Notes

This header exposes detailed drive health, topology, enclosure, security, and progress state. It is firmware-layout sensitive and uses packed structs throughout.
