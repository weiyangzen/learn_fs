# File Research: sources/os/bsd/openbsd-src/sbin/disklabel/dkcksum.c

## Purpose
`dkcksum.c` computes the OpenBSD disklabel checksum.

## Main API
- `dkcksum(const struct disklabel *lp)`: XORs 16-bit words from the start of the disklabel through the configured partition array end, using `d_npartitions` to determine the endpoint.

## Integration Notes
`disklabel.c` sets `d_checksum` to zero, calls `dkcksum()`, then writes the resulting checksum before issuing `DIOCWDINFO`.

## Risk Notes
The checksum covers only partitions up to `d_npartitions`; callers must ensure `d_npartitions` is valid before computing/writing the label.
