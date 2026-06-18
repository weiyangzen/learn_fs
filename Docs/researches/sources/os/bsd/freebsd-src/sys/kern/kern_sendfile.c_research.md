# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_sendfile.c

Read completely: 1322 lines.

## Purpose
Implements `sendfile(2)` and `vn_sendfile()`, moving file or shared-memory VM object pages to stream sockets with minimal copying, optional headers/trailers, asynchronous page-in, not-ready mbufs, readahead, `SF_NOCACHE`, and KTLS integration.

## Main Elements
- Defines `struct sf_io` to track one sendfile batch: in-flight I/O refcount, error state, socket, mbuf chain, VM object, base page index, pages, and optional KTLS state.
- Allocates and exports `sfstat` counters under `kern.ipc.sfstat`, with writable sysctl reset support.
- Provides mbuf external free callbacks for mapped `sf_buf` mbufs and unmapped `M_EXTPG` mbufs, releasing pages and optionally trying to free them for `SF_NOCACHE`.
- `xfsize()`, `vmoff()`, and `fixspace()` calculate per-page payload lengths, object offsets, and socket-space adjustments after page or `sf_buf` allocation failures.
- `sendfile_iowait()` waits for async page-ins to drain before unwiring pages on failure paths.
- `sendfile_iodone()` is the async pager completion callback and final completion path: restores bogus-page placeholders, unbusies pages, handles I/O errors by aborting the socket, notifies protocol readiness with `pr_ready()`, or queues software KTLS encryption work.
- `sendfile_swapin()` grabs and wires needed object pages, validates cached pages, zero-fills sparse/no-page regions, launches async pager reads for invalid runs, uses bogus pages for already-valid pages inside pager runs, records readahead stats, and recovers pages on I/O setup failure.
- `sendfile_getobj()` accepts only vnode regular files and shared-memory descriptors with VM objects, obtains object size safely, rejects dead objects, and takes a temporary VM object reference.
- `sendfile_getsock()` resolves the target descriptor with send rights, requires a connected stream socket, and rejects SCTP one-to-one sockets.
- `sendfile_wait_generic()` checks send-buffer state, adjusts auto low-water marks, handles nonblocking `EAGAIN`, waits for space, and reports socket errors/closed connection.
- `vn_sendfile()` is the core loop: gets source object and socket, performs MAC send checks, locks socket sending, holds KTLS session state, copies optional headers into mbufs, revalidates vnode size, computes socket-space-sized page batches and readahead, swaps pages in, builds either mapped `EXT_SFBUF` mbufs or unmapped `M_EXTPG` chains, marks not-ready pages when I/O is pending, frames TLS records, sends through protocol `pr_send()`, and updates byte counts.
- Handles trailers by releasing the socket send lock and delegating to `kern_writev()`.
- `sendfile()` copies in user `sf_hdtr`, handles FreeBSD 4 header-size compatibility, obtains the source fd with `CAP_PREAD`, calls fileops `fo_sendfile()`, and copies out `sbytes`.
- `sys_sendfile()` and optional `freebsd4_sendfile()` provide syscall entry points.

## Dependencies And Integration
Highly integrated with VM objects, vnode pager state, shared memory objects, `vm_page_grab_pages_unlocked()`, async pager I/O, socket send-buffer locking, protocol `pr_sendfile_wait`/`pr_send`/`pr_ready`, mbuf external storage, `sf_buf`, KTLS, MAC checks, Capsicum rights, audit, inotify access events, TCP logging, and VNET context switching.

## Risk Notes
Risk is concentrated around page lifetime and async I/O: pages must stay wired until mbufs free them, bogus-page substitution must be restored correctly, vnode/object size changes must not expose beyond EOF, and socket abort/error paths must free not-ready mbufs. Header/trailer accounting, KTLS references, and `SF_NODISKIO`/`SF_NOCACHE` partial-progress cases require careful byte-count and cleanup behavior.
