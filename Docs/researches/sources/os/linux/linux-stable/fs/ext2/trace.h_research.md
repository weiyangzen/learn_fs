# File Research: sources/os/linux/linux-stable/fs/ext2/trace.h

## Purpose

Declares ext2 trace events for direct I/O read/write paths.

## Main Responsibilities

- Sets `TRACE_SYSTEM ext2`.
- Defines an event class `ext2_dio_class` for common direct I/O fields.
- Defines direct I/O read/write events from that class.
- Defines a distinct endio event for write completion.

## Key Trace Events

- `ext2_dio_write_begin`
- `ext2_dio_write_end`
- `ext2_dio_write_buff_end`
- `ext2_dio_read_begin`
- `ext2_dio_read_end`
- `ext2_dio_write_endio`

## Captured Fields

The common event class records:

- Device major/minor.
- Inode number.
- File size.
- I/O position.
- Requested iterator count.
- `ki_flags`.
- Whether the I/O is async.
- Return value.

`ext2_dio_write_endio` records similar context but uses completed size and integer return status.

## Dependencies

- Uses `<linux/tracepoint.h>`.
- Uses `file_inode()`, `iov_iter_count()`, `is_sync_kiocb()`, and `TRACE_IOCB_STRINGS`.
- Ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE trace`, and `<trace/define_trace.h>`.

## Research Notes

The tracepoints are focused narrowly on direct I/O observability, not broad ext2 metadata tracing. They are useful for correlating direct I/O submission/completion with inode size, position, length, flags, and async status.
