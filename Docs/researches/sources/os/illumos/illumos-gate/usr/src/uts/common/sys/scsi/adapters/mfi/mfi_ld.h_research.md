# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_ld.h

## Role

MFI logical-drive and RAID configuration definition header.

## Key Elements

- Defines spare flags, logical-drive states, initialization modes, access policies, cache policy bits, and maximum array/row/span sizes.
- `mfi_array_t` describes one array: size, drive count, reference, padding, and per-row physical drive references/state/enclosure location.
- `mfi_spare_t` describes a spare drive, spare type, and associated array references.
- `mfi_ld_ref_t` identifies a logical drive by target ID and sequence number.
- `mfi_ld_list_t` returns all logical drives with reference, state, and size.
- `mfi_ld_parameters_t` stores RAID levels, stripe, drive count, span depth, state, init state, consistency, and SSD cache flag.
- `mfi_ld_properties_t` stores logical drive reference, name, cache/access/disk-cache policies, background-init flag, and reserved bytes.
- `mfi_span_t` describes logical-drive spans over arrays.
- `mfi_ld_config_t` combines properties, parameters, and spans.
- `mfi_ld_progress_t` reports active consistency-check, background-init, foreground-init, and reconstruction progress.
- `mfi_ld_info_t` combines logical-drive config, size, progress, cluster owner, reconstruction state, VPD page 83 data, and reserved space.
- `mfi_ld_tgtid_list_t` and `mfi_config_data_t` are variable-length wrappers for target IDs and full RAID configuration data.

## Dependencies and Coupling

Includes `mfi.h` and `mfi_pd.h` because logical-drive configuration embeds physical-drive references. Uses packed structures and size assertions for firmware layout.

## Research Notes

`mfi_config_data_t` has multiple zero-length arrays representing arrays, logical drives, and spares in one firmware buffer. Consumers must use the count/size fields to walk it safely.
