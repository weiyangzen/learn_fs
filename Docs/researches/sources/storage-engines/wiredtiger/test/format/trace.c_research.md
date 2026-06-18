# sources/storage-engines/wiredtiger/test/format/trace.c

Purpose: configures and owns an auxiliary WiredTiger log database used for operation/message tracing.

Important APIs and functions: `trace_config`, `trace_init`, and `trace_teardown`. It recognizes trace options `all`, `bulk`, `cursor`, `mirror_fail`, `read`, `timestamp`, `txn`, and `retain=<n>`.

Control flow: `trace_config` duplicates the config string, marks recognized tokens as consumed, sets flags and retention, rejects leftover non-comma/non-space characters, then enables tracing. `trace_init` creates `g.home/OPS.TRACE`, opens a logging-enabled WiredTiger connection with log removal and retention, opens a global session, and initializes a spinlock. `trace_teardown` nulls `g.trace_conn`, destroys the lock, and closes the trace connection.

State and persistence: mutates `g.trace_flags`, `g.trace_retain`, `g.trace_conn`, `g.trace_session`, and `g.trace_lock`. Persists trace logs under `OPS.TRACE` with retained log files and statistics logs.

Dependencies and integration: selected by `t.c -T`; used by trace macros in `format_inline.h`, event handling in `wts.c`, and session wrappers in `format_util.c`.

Risks and test signals: config parsing is substring-based and consumes recognized words in a copy, so option names must remain unambiguous. Teardown must tolerate being called during failure and normal shutdown. Trace retention defaults to at least 10 files.
