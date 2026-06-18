# sources/test-tools/fio/engines/falloc.c

Purpose: Implements a synchronous `falloc` engine that models IO with `fallocate()` operations rather than data transfer.

Important APIs/functions: Custom `open_file()` opens files/block devices read-write with fio's file hash. `fio_fallocate_queue()` maps fio directions to fallocate modes. The registered engine uses generic close/size callbacks and `FIO_SYNCIO | FIO_SYNCFS`.

Control flow: Open rejects non-file/non-block targets and stdin/stdout, uses `file_lookup_open()` and `add_file_hash()` to share descriptors, and records errors through `td_verror()`. Queue performs read as `FALLOC_FL_KEEP_SIZE`, write as extending fallocate mode `0`, trim as `FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE`, and sync directions through `do_io_u_sync()`. Errors set `io_u->error = errno`.

State/persistence: File allocation changes persist in the filesystem or block device. No extra engine state is stored.

Dependencies/integration: Depends on Linux fallocate flags, fio file hash, generic close/size, sync helpers, and read-only checks.

Risks: Requires filesystem support for selected fallocate modes. Opening block devices with `O_CREAT` is harmless or platform-dependent but unusual. Data is not read/written, so verification semantics differ from real IO.

Test signals: Exercise file and block targets, trim hole punching support, sync directions, unsupported filesystem errors, and file hash reuse.
