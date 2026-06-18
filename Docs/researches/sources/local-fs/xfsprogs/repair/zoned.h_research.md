# File Research: sources/local-fs/xfsprogs/repair/zoned.h

Header for zoned realtime device validation.

Exports:
- `check_zones(struct xfs_mount *mp)`

Used by repair setup or realtime validation paths to ensure zoned block-device layout matches rtgroup metadata expectations.
