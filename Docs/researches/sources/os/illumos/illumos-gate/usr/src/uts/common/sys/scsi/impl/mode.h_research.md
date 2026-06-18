# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/mode.h

This implementation-specific mode header defines legacy and vendor-specific mode sense/select variants.

Key definitions:
- Defines `modeheader_seq` for sequential-access mode headers.
- Defines CCS-era direct-access error recovery page `mode_err_recov_ccs`.
- Maps `_reserved_ins` to `ins` for CCS format-page compatibility.
- Defines SCSI-2 cache page `mode_cache` and CCS cache page `mode_cache_ccs`.
- Defines older SCSI-2 control page `mode_control`.
- Defines Emulex MD21 vendor-unique format parameters.
- Defines CD-ROM speed mode page constant and `mode_speed`.

Dependencies:
- Included by `generic/mode.h`, relying on prior definitions of `struct mode_page` and `struct block_descriptor`.

Impact:
- Preserves compatibility with older device mode-page formats and vendor-specific direct-access hardware.

Cautions:
- Multiple structures are explicitly incompatible with newer generic versions; consumers must use returned mode-page length/version to select the correct layout.
- Contains legacy hardware-specific definitions that should not be generalized to modern devices.
