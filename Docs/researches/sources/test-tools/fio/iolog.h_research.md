# sources/test-tools/fio/iolog.h

Purpose: public contract for fio iolog replay pieces and statistical log buffers. It defines sample encoding, log metadata, IO history records, compression chunk records, and exported log/replay APIs used by the backend, stats, verify, and output paths.

Important APIs/types: `struct io_stat`, `io_hist`, `io_sample`, `io_logs`, `io_log`, `io_piece`, `log_params`, and `iolog_compress`. Macros encode optional sample fields in high bits of `__ddir` (`LOG_OFFSET_SAMPLE_BIT`, `LOG_PRIO_SAMPLE_BIT`, `LOG_AVG_MAX_SAMPLE_BIT`, `LOG_ISSUE_TIME_SAMPLE_BIT`) and compute variable sample sizes via `log_entry_sz`, `log_sample_sz`, and `get_sample`.

Control flow/state: callers initialize `io_piece` with `init_ipo`, queue or store it, and later replay or verify from lists/trees. Callers create `io_log` objects through `setup_log`, append samples elsewhere in fio, and flush or free them through the declared functions. `per_unit_log` and `inline_log` guide writeout and aggregation behavior.

Dependencies/integration: exposes fio-specific types from `rbtree.h`, `ieee754.h`, `flist.h`, and `ioengines.h`. `struct io_log` embeds pthread mutexes for compressed chunks and deferred frees, binding users to pshared/threaded log handling.

Risks/test signals: the flexible-array `aux[]` layout requires every producer/consumer to agree on optional fields. `ipo_bytes_align` assumes power-of-two replay alignment. Test coverage should exercise offset/priority/issue-time combinations, histogram samples, compressed logs, and replay file actions.
