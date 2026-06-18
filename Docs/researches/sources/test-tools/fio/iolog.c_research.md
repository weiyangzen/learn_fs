# sources/test-tools/fio/iolog.c

Purpose: implements fio IO logging, replay, runtime sample flushing, and optional compressed log storage. It supports writing version 3 textual iologs, reading version 2/3 iologs or blktrace inputs, queueing replay `io_piece` records, and persisting latency/bandwidth/IOPS/histogram logs.

Important APIs/functions: `init_iolog`, `read_iolog_get`, `log_io_u`, `log_file`, `log_io_piece`, `unlog_io_piece`, `trim_io_piece`, `setup_log`, `flush_samples`, `flush_log`, `td_writeout_logs`, `fio_writeout_logs`, `iolog_compress_init/exit`, `iolog_file_inflate`, and `log_chunk_sizes`. Internal helpers parse versioned iolog lines, handle open/close/unlink pseudo-IOs, generate replay delays, serialize samples, and compress/decompress chunks with zlib when configured.

Control flow: initialization chooses read, write, or no-op mode. Replay reads file/socket/stdin headers, parses records into `td->io_log_list`, then `read_iolog_get` dequeues pieces into `io_u` objects, applying file actions and replay timing. Verification logging inserts successful writes into a list or red-black tree depending on overlap risk. Runtime logging accumulates samples in `struct io_log`, optionally hands full buffers to a compression workqueue, and final writeout locks per-file log names before flushing or sending logs to server/GUI clients.

State/persistence: mutates `thread_data` replay cursors, timing offsets, total IO size, max block sizes, IO history trees/lists, compression chunk lists, pending sample buffers, and output files. Textual iologs are append-created with a version line; normal logs may append or overwrite depending on `per_job_logs` and compressed-store mode.

Dependencies/integration: tightly integrated with `fio.h`, file lifecycle helpers, trim tracking, blktrace, data placement, pshared mutexes, workqueues, server output, `lib/rbtree`, `lib/roundup`, zlib, Unix sockets, and fio's runstate machine.

Risks/test signals: parsing uses fixed 256-byte `%s` file/action buffers and line-oriented input; malformed actions are logged and skipped. Compression depends on ordered chunk sequence and deferred frees, so leaks or stale pointers are possible around async paths. Replay timing can drift through `time_offset`. Signals are successful replay/writeout, decompression compatibility, no duplicate verification pieces after overlap pruning, and no lost samples when logs regrow or compress.
