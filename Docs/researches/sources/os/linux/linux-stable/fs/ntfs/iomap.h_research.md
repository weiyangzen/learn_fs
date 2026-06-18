# File Research: sources/os/linux/linux-stable/fs/ntfs/iomap.h

## Summary
Declares the NTFS iomap integration surface used by the rest of the driver.

## Main Contents
Includes Linux pagemap/iomap headers plus NTFS volume and inode declarations, then exports the NTFS iomap operation tables for writes, reads, seeks, page-mkwrite, direct I/O, writeback, folio operations, and device zeroing.

## Key Interfaces
- `ntfs_write_iomap_ops`.
- `ntfs_read_iomap_ops`.
- `ntfs_seek_iomap_ops`.
- `ntfs_page_mkwrite_iomap_ops`.
- `ntfs_dio_iomap_ops`.
- `ntfs_writeback_ops`.
- `ntfs_iomap_folio_ops`.
- `ntfs_dio_zero_range()`.

## Risks
This header exposes shared operation-table symbols only; behavioral correctness depends on callers selecting the correct table for buffered I/O, DIO, seek, page fault, or writeback semantics.
