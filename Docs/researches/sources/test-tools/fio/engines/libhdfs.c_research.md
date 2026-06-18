# sources/test-tools/fio/engines/libhdfs.c

## Purpose
Implements an HDFS-backed fio engine using libhdfs. Because HDFS files are append-oriented and not normally mutable in-place, the engine maps a logical fio file into many fixed-size chunk files and selects the chunk by the fio offset to approximate random reads and writes.

## Important APIs, Types, And Functions
`struct hdfsio_data` stores the HDFS filesystem handle, currently open HDFS file handle, and current chunk id. `struct hdfsio_options` provides namenode host/port, working directory, chunk size, single-instance behavior, and direct-read selection. Key functions are `get_chunck_name()`, `fio_hdfsio_setup()`, `fio_hdfsio_init()`, `fio_hdfsio_io_u_init()`, `fio_hdfsio_prep()`, `fio_hdfsio_queue()`, `fio_hdfsio_open_file()`, `fio_hdfsio_close_file()`, and `fio_hdfsio_io_u_free()`.

## Control Flow
`setup` allocates engine state and computes logical file sizes from fio size/filesize options. `init` builds and connects an HDFS client, optionally forcing a new instance, and sets the working directory after checking existence. `io_u_init` pre-creates chunk files for each fio file, writing zero-filled buffers until every chunk reaches the configured size. `prep` maps `io_u->offset` to a chunk id, closes the previous chunk if necessary, chooses read or write flags, opens the chunk, and stores it as current. `queue` seeks within the chunk, performs `hdfsRead()`, `readDirect()`, `hdfsWrite()`, or `hdfsFlush()`, and completes synchronously.

## State And Persistence
Logical fio file state is persisted as HDFS paths named `file_name_chunkid`. The engine tracks only one open chunk per thread. `curr_file_id == -1` means no current file. File sizes are logical and set in fio metadata, not queried from HDFS except during chunk preparation.

## Dependencies And Integration Points
Depends on libhdfs and fio diskless/sync engine hooks. It avoids generic POSIX open/close and marks itself `FIO_SYNCIO | FIO_DISKLESSIO | FIO_NODISKUTIL`.

## Risks
The code uses the misspelled `chunck` naming throughout, which matters for option aliasing and path formatting. `io_u_free` disconnects the HDFS filesystem, so lifecycle correctness depends on fio calling it in a safe order relative to all `io_u` objects. `hdfsGetPathInfo()` results are not freed in the source. Random writes smaller than chunks can fail because HDFS seek/write semantics are limited. `fio_hdfsio_open_file()` sets `td->error` for `direct` but returns 0.

## Test Signals
Test chunk creation for multiple files, exact and non-exact logical size to chunk-size division, read/write/sync paths, `hdfs_use_direct`, missing directory/host failures, `single_instance=0`, random write behavior across chunk boundaries, close/reopen chunk transitions, and cleanup/disconnect behavior.
