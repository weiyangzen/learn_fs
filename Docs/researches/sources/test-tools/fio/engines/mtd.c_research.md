# sources/test-tools/fio/engines/mtd.c

## Purpose
Implements a synchronous fio engine for Linux MTD character devices. It splits each request across erase-block boundaries, performs MTD read/write/erase operations through libmtd/oslib helpers, and can skip known bad erase blocks.

## Important APIs, Types, And Functions
Global `desc` is the libmtd descriptor opened at engine registration. `struct fio_mtd_data` stores `mtd_dev_info` per file. `struct fio_mtd_options` exposes hidden `skip_bad`. Important functions are `fio_mtd_queue()`, `fio_mtd_maybe_mark_bad()`, `fio_mtd_is_bad()`, `fio_mtd_open_file()`, `fio_mtd_close_file()`, and `fio_mtd_get_file_size()`.

## Control Flow
Registration opens libmtd. File open uses generic open, allocates per-file MTD data, and queries device info. Queue loops over the `io_u` buffer, computing erase-block index and offset, limiting each sub-operation to the current erase block. With `skip_bad`, it checks and silently skips bad blocks. Reads call `mtd_read()`, writes call `mtd_write()`, trims require whole erase-block alignment and call `mtd_erase()`. On `EIO`, the engine attempts to mark the erase block bad.

## State And Persistence
Per-file engine data caches erase-block size and total MTD size. Persistent effects are writes, erases, and marking blocks bad. Skipped bad-block ranges still advance through the request without transferring data.

## Dependencies And Integration Points
Depends on Linux MTD UAPI, fio's oslib libmtd wrapper, generic file helpers, and synchronous fio queue completion.

## Risks
Partial failures can leave `io_u->error` set while the loop advances to later erase blocks. Trim alignment is checked per erase block but the loop continues unless a helper failure breaks it. Bad-block marking only happens for `errno == EIO`. The global libmtd descriptor must be valid for all engine users.

## Test Signals
Test reads/writes spanning multiple erase blocks, trim alignment failures and aligned erases, `skip_bad=1`, simulated `EIO` bad-block marking, file-size discovery, open failure cleanup, and registration/unregistration descriptor lifecycle.
