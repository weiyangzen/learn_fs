# sources/test-tools/fio/engines/ime.c

Purpose: Implements three DDN Infinite Memory Engine fio engines: `ime_psync`, `ime_psyncv`, and `ime_aio`, using IME native APIs instead of POSIX IO.

Important APIs/functions: Shared helpers handle IME filename prefixing, file size/open/close/unlink, setup, engine init/finalize, and event lookup. `ime_psync` uses blocking `ime_native_pread/pwrite/fsync`. `ime_psyncv` batches contiguous IOs into one preadv/pwritev request with commit/getevents. `ime_aio` batches contiguous iovecs into async IME requests with callback-driven completion. Registration exposes all three engines.

Control flow: Setup initially sets file sizes to zero to avoid POSIX sizing before fork/thread setup. Engine init calls `ime_native_init()`, marks global initialized, and temporarily sets fio file sizes to desired IO extents. Open prefixes filenames with `DEFAULT_IME_FILE_PREFIX`, rejects trim, maps fio flags, opens through IME, sizes/truncates write files as needed, and rejects too-small read files. Psync completes immediately per queue. Psyncv queues only contiguous same-fd/same-direction iovecs until commit, then reports events after the blocking vector call. AIO queues iovecs into a ring, starts one or more `ime_native_aio_read/write` requests on commit, and `getevents()` waits on per-request condition variables until completions arrive.

State/persistence: Global `fio_ime_is_initialized` tracks process/thread-level IME initialization. Per-engine `ime_data` stores iovec rings, `io_u` arrays, event arrays, queue indices, last offset, and either sync or async request state. IME files persist through native storage and prefixed filenames.

Dependencies/integration: Requires `ime_native.h`, pthread condition/mutex primitives, fio queue/commit/getevents contracts, diskless flags to avoid POSIX paths, and native IME lifecycle calls.

Risks: Global initialization flag is not locked and may race in thread mode. Several allocations in psyncv/aio init are unchecked. Psyncv completion loops over `queued` using linear indices even though ring fields exist, which is safe only because it resets after each commit. AIO residual calculation distributes aggregate bytes over iovecs and may be confusing for partial completions. `fio_ime_unlink_file()` calls POSIX `unlink()` on the prefixed path rather than an IME native unlink.

Test signals: Validate all three engines with read/write/sync, contiguous and non-contiguous batching, iodepth ring wrap, async callback errors, fork versus thread lifecycle, too-small read rejection, file extension, and trim rejection.
