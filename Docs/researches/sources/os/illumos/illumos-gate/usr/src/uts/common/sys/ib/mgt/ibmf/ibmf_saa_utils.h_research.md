# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_saa_utils.h

## Scope

Declares SAA utility functions for packing/unpacking SA headers and payloads and parsing selected subnet-management trap buffers.

## APIs

- `ibmf_saa_utils_pack_sa_hdr()` packs an `ib_sa_hdr_t` into a wire-format class header buffer.
- `ibmf_saa_utils_unpack_sa_hdr()` unpacks a wire-format class header buffer into an `ib_sa_hdr_t`.
- `ibmf_saa_utils_unpack_payload()` converts wire-format SA payload bytes into host-format record structures for a given attribute ID, attribute offset, and response type.
- `ibmf_saa_utils_pack_payload()` converts host-format payload structures into wire-format SA payload bytes.
- Trap parsers:
  - `ibmf_saa_gid_trap_parse_buffer()`
  - `ibmf_saa_capmask_chg_trap_parse_buffer()`
  - `ibmf_saa_sysimg_guid_chg_trap_parse_buffer()`

## Dependencies

- Includes `sys/ib/mgt/sa_recs.h`.
- The header states the packing definitions are based on InfiniBand specification version 1.1 and must be updated with spec changes.

## Risks And Invariants

- Correct packing depends on attribute ID and known SA record layout; unknown or changed attributes require utility updates.
- Callers control allocation behavior through `km_sleep_flag`.
- Trap parsers assume buffers contain the expected trap record format.
