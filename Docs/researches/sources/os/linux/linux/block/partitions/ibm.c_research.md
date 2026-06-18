# File Research: sources/os/linux/linux/block/partitions/ibm.c

## Summary
Implements IBM s390 DASD partition recognition for VOL1, LNX1, and CMS1 labels.

## Main Responsibilities
- Locates DASD volume labels across ECKD, FBA, and CMS-formatted FBA layouts.
- Converts EBCDIC label type and volume IDs to ASCII.
- Parses VTOC format labels for VOL1 disks.
- Creates single Linux partitions for LNX1 and CMS1 labels.
- Uses DASD geometry and optional DASD driver metadata for compatibility cases.

## Key APIs
- `ibm_partition()`.
- Internal helpers: `find_label()`, `find_vol1_partitions()`, `find_lnx1_partitions()`, `find_cms1_partitions()`.

## Important Behavior
`find_label()` checks label sectors determined by DASD metadata when available, otherwise tries three known candidate locations. VOL1 parsing walks VTOC format 1/8 labels and skips format 4/5/7/9 labels.

LNX1 creates one partition after the label. For older LDL formats without large-volume support, it reconciles geometry-derived size with actual disk sectors and DASD metadata. CMS1 handles both reserved minidisks and ordinary CMS labels, including the FBA DIAG special case where the label may be at sector 1.

If DASD metadata is present but no valid label is found, the parser still claims DASD disks for backward compatibility and can synthesize an LDL partition.

## State and Dependencies
Uses `disk->fops->getgeo()` and dynamically resolves `dasd_biodasdinfo` with `symbol_get()`. Allocates temporary DASD info, geometry, and label buffers.

## Risks
Correct extents depend on DASD geometry conversion from CCHH/CCHHB values. The compatibility fallback deliberately claims unlabeled DASD devices, which is unusual compared with most partition recognizers.
