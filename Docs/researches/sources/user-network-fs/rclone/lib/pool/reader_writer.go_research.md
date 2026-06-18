# sources/user-network-fs/rclone/lib/pool/reader_writer.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/reader_writer.go -->
## sources/user-network-fs/rclone/lib/pool/reader_writer.go

Purpose: implements `RW`, a pool-backed append-only in-memory FIFO that supports `io.Reader`, `io.Writer`, `io.ReaderFrom`, `io.WriterTo`, `io.Seeker`, `io.Closer`, and delayed read accounting. It is designed for buffering data through reusable pool pages while allowing reads and writes to run concurrently.

Important APIs and control flow: `NewRW(pool)` initializes state and a nonblocking write-signal channel. `Reserve(n)` preallocates enough pages for later writes. `Write` and `ReadFrom` append data page by page, growing from reserved pages or `Pool.Get`, updating `size` and `lastOffset`, and signalling waiters. `Read` and `WriteTo` consume from read offset `out`, fetch the current page with `readPage`, update accounting via `accountRead`, and return `io.EOF` when `out >= size`. `Seek` changes only read position and rejects invalid whence, negative positions, or seeking past written data. `WaitWrite(ctx)` waits for data, cancellation, or a one-second timeout. `Close` returns written and reserved pages to the pool.

State, dependencies, and integration: a mutex protects shared `pages`, `size`, `lastOffset`, and reserved pages during page selection and metadata changes. `account`, `accountOn`, `reads`, and `out` drive byte accounting, with `DelayAccounting` useful when initial rereads are hash/checksum passes. The type integrates with `io.Copy` through `ReadFrom` and `WriteTo`.

Risks and test signals: `out` is written without consistently holding `mu`, so the design supports one reader and one writer rather than arbitrary concurrent readers. `Reserve` is documented as safe only once. `Close` should be called to return buffers. Tests cover basic I/O, seeking errors, accounting errors/delay, page-boundary sizes, `ReadFrom`/`WriteTo`, and concurrent read/write patterns.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/reader_writer.go -->
