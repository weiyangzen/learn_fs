# File Research: sources/os/linux/linux/io_uring/rw.c

Read/write operation implementation. This file handles scalar, vectored, fixed-buffer, vectored-fixed, multishot read, metadata/protection-information, iopoll, page-lock retry, and completion cleanup paths.

Key responsibilities:
- Prepares read/write SQEs into `struct kiocb`, buffer indexes, ioprio, write streams, rw flags, and optional PI metadata.
- Imports user buffers, provided buffers, registered fixed buffers, and registered fixed iovec vectors.
- Executes reads through `read_iter` or legacy `read`, and writes through `write_iter` or legacy `write`.
- Handles NOWAIT probing, poll-based retry, io-wq retry, page-unlock async retry, and partial I/O accounting.
- Implements multishot reads with provided buffers and poll retry integration.
- Implements iopoll and hybrid iopoll completion harvesting.
- Recycles async read/write state and iovec storage.

Important data flows:
- Prep allocates `io_async_rw`, stores SQE fields, imports buffers unless deferred for buffer selection/fixed buffers, and saves iterator state for retry.
- Read issue imports late buffers if needed, initializes file/kiocb state, verifies area, calls the read operation, handles `-EAGAIN`, partial buffered reads, and completion.
- Write issue initializes file state, starts write accounting for regular files, verifies area, calls write operation, handles partial writes by recording `bytes_done`, and retries blocking if necessary.
- Completion paths combine current result with `bytes_done`, release provided buffers, send fsnotify access/modify events, end write accounting, and recycle async state.
- IOPOLL walks `ctx->iopoll_list`, invokes either file `iopoll` or uring_cmd iopoll, moves completed requests to batched completions, and flushes CQEs.

Concurrency and locking:
- Normal async completions schedule task_work through `io_complete_rw()`.
- IOPOLL completion uses release/acquire ordering on `req->iopoll_completed`.
- Cleanup deliberately avoids fast recycling for io-wq/refcounted requests to prevent UAF with lower layers that inspect iterators after queuing completion.
- Page-lock retry installs a `wait_page_queue` and requeues task_work when the page unlocks.

Important invariants:
- NOWAIT requests must not silently block; unsupported paths return `-EAGAIN`.
- PI metadata is supported only with files advertising metadata support and direct I/O.
- Multishot read requires provided buffers and a pollable file.
- Fixed-buffer imports must respect registered buffer direction and range.
- Stream files use NULL position; non-stream `ki_pos == -1` uses and updates `file->f_pos`.

Notable risks:
- Partial read/write retry depends on restored iterator and metadata state.
- Legacy `read`/`write` fallback cannot support iopoll and rejects kernel-backed fixed bvec buffers.
- Buffered async retry uses a union with metadata fields, so metadata and buffered waitqueue retry cannot coexist.
