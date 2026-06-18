# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/part.h

Declares fdisk’s partition geometry and internal partition records.

Key structures:
- `struct chs` stores cylinder/head/sector coordinates.
- `struct prt` stores internal partition state: base sector, sector count, boot flag, and partition ID.

Exports:
- MBR/GPT partition type menu printers.
- DOS partition to internal partition conversion, and reverse conversion.
- Partition table header and row printers.
- GPT UUID description and parser helpers.
- GPT protected-type check.
- LBA-to-CHS conversion.

The header is consumed by fdisk modules that need partition display, editing, conversion, and type lookup without embedding the large tables from `part.c`.
