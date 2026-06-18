# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_xio.c

Implements the kernel XIO abstraction: a vmspace-agnostic collection of held `vm_page_t` pages used to pass user or kernel data between threads without permanently mapping it into kernel virtual memory.

Key APIs:
- `xio_init()`
- `xio_init_kbuf()`
- `xio_init_pages()`
- `xio_release()`
- `xio_uio_copy()`
- `xio_copy_xtou()`
- `xio_copy_xtok()`
- `xio_copy_utox()`
- `xio_copy_ktox()`

Important behavior:
- `xio_init()` creates an empty XIO using internal page storage.
- `xio_init_kbuf()` translates a kernel buffer to physical pages with `pmap_kextract()`, converts to `vm_page_t`, holds pages, and records byte count/page offset. Failure releases all held pages and returns `EFAULT`.
- `xio_init_pages()` holds a caller-provided page array and records total bytes.
- `xio_release()` dirties pages if `XIOF_WRITE` is set, unholds pages, clears counters, and marks error `ENOBUFS`.
- `xio_uio_copy()` copies between XIO pages and a `uio` using `uiomove_fromphys()`.
- `xio_copy_xtou()` maps pages one at a time with `lwbuf`, then `copyout()`s to user memory.
- `xio_copy_xtok()` maps pages with `lwbuf` and `bcopy()`s to kernel memory.
- `xio_copy_utox()` maps pages and `copyin()`s user data into XIO pages.
- `xio_copy_ktox()` maps pages and `bcopy()`s kernel data into XIO pages.

Safety notes:
- Comments warn that user memory cannot be mapped directly into XIO unless it uses managed pages, or modifications race pageout/flush.
- TODO notes mention missing busy-page and writable checks for modification paths.

Filesystem relevance:
- Explicitly intended for I/O path and VFS use. It is a page-backed transfer object for moving file data across threads or contexts without tying buffers to the original vmspace.
