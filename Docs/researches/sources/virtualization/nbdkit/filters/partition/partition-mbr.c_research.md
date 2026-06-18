# File Research: sources/virtualization/nbdkit/filters/partition/partition-mbr.c

This file locates primary and logical MBR partitions. It decodes the four-byte little-endian start-sector and sector-count fields from partition table entries and treats type bytes `0x05`, `0x0f`, and `0x85` as extended partitions.

For primary partitions `1..4`, `find_mbr_partition` returns the first matching non-empty, non-extended entry and rejects GPT protective type `0xEE` with guidance about possible sector-size mismatch. For logical partitions, it finds the enclosing extended partition, follows the EBR chain starting at partition number 5, reads each EBR sector, validates alignment and bounds, rejects non-increasing EBR links, and ensures logical partitions stay within the extended partition extent.

Risk controls are stronger for EBR chains than for primary MBR metadata: malformed chains are rejected when they point outside the disk, point to the MBR, loop backward, or describe partitions outside the enclosing extended partition. The code intentionally does not accept unusual valid tables with reverse-ordered EBR chains.
