# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_disklabel64.c

DragonFly 64-bit disklabel operations implementation with byte-granular offsets, UUIDs, CRC validation, and modern alignment defaults.

Key responsibilities:
- Reads disklabel64 metadata from offset 0 of the slice/device, using a sector-rounded I/O size.
- Validates magic, partition count, and CRC over the active disklabel64 region.
- Exposes partition bounds by converting byte offsets/sizes to media blocks.
- Loads per-partition filesystem type UUIDs, storage UUIDs, and legacy filesystem type values.
- Validates and applies new labels while preventing open partitions from moving, shrinking, or changing UUIDs.
- Writes labels with read-modify-write so reserved leading bytes not covered by the label payload are preserved.
- Creates compatibility labels and virgin labels, including storage UUID generation, boot area reservation, backup-label reservation, and 1 MiB physical alignment.

Important behavior:
- Partition offsets and sizes must be aligned to `dss_secsize`.
- Virgin labels reserve room for the label, stage2 boot area, and backup label area, and align usable partition space relative to the physical disk start.
- `l64_adjust_label_reserved()` write-protects the label area of a slice based on `d_bbase`.

Dependencies:
- Depends on `disklabel64`, disk slice state, kernel UUID generation, CRC32, pbuf synchronous I/O, and buffer helpers.

Notable risks:
- The label is sector-agnostic but still assumes the rounded label I/O fits in a pbuf.
- The read path derives the CRC span from the on-disk partition count before rejecting too-large counts, so corrupted counts rely on the surrounding validation and buffer sizing assumptions.
- Open partitions can grow but cannot move, shrink, or change type/storage UUIDs.
