# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fdbuffer.c

## Purpose
Implements `fdbuffer_t`, a filesystem/direct-I/O helper abstraction that wraps either page lists or user virtual-address buffers and tracks cloned `buf_t` I/O, holes, async completion, errors, and final byte accounting.

## Main Responsibilities
- Create fdbuffers for page I/O or virtual-address I/O.
- Build cloned buf structures for subrange I/O.
- Track outstanding async I/O count and completion callbacks.
- Account attempted/completed/residual bytes.
- Record and optionally zero sparse holes.
- Free parent pageio/physical buf resources.

## Allocation and Initialization
`fdb_init()` creates `fdb_cache`.

`fdb_cache_constructor()` / destructor initialize/destroy `fd_mutex`.

`fdb_prepare()` resets reusable fields: holes, callbacks, parent buffer, residual, I/O count, dispatch count, and error state.

Creation:
- `fdb_page_create(page_t *pp, size_t len, int flags)` creates an `FDB_PAGEIO` buffer.
- `fdb_addr_create(caddr_t addr, size_t len, int flags, page_t **pplist, proc_t *procp)` creates an `FDB_VADDR` buffer.

Both require read or write mode.

## I/O Setup
`fdb_iosetup()`:
- Validates direction against fdb state and enforces sync/async consistency.
- Marks sync or async mode and increments `fd_iodispatch`.
- Creates a parent buf once:
  - `pageio_setup()` for page I/O.
  - allocated `buf_t` with `bioinit()`, `B_BUSY | B_PHYS`, optional `B_SHADOW` for virtual-address I/O.
- Clones a subrange with `bioclone()`.
- Stores the `fdbuffer_t` in `bp->b_forw`.
- Sets `B_ASYNC` and callback to `fdb_iodone()` for async I/O.

## Completion
`fdb_iodone(buf_t *bp)`:
- Maps out remapped buffers.
- Decrements outstanding dispatch count.
- Records error and residual bytes.
- Adds completed/attempted byte count.
- If no more dispatches and final state is `FDB_ERROR` or `FDB_DONE`, invokes callback for async or immediate-callback mode.
- For `FDB_ICALLBACK`, callback can fire per buffer.
- Frees cloned buf with `freerbuf()`.

`fdb_ioerrdone()`:
- Marks an async fdb done or errored without a buf completion.
- If no outstanding dispatches remain, invokes callback.

`fdb_get_iolen()`:
- Returns `fd_iocount - fd_resid`, requiring no outstanding dispatches.

`fdb_get_error()` returns the stored error.

## Hole Handling
`fdb_add_hole()`:
- Inserts a hole descriptor in ascending offset order.
- Adds hole length to `fd_iocount` so holes count toward accounted I/O range.
- Requires `off < fd_len`.

`fdb_get_holes()`:
- If `FDB_ZEROHOLE`, zeros holes before returning the list.

`fdb_zero_holes()`:
- For `FDB_PAGEIO`, walks page list and calls `pagezero()` for hole ranges.
- For `FDB_VADDR`, calls `bzero()` on buffer ranges.
- Frees hole records as it processes them.
- Panics for unknown fdb type.

## Freeing
`fdb_free()`:
- Zeroes holes if requested.
- Frees remaining hole records.
- Calls `pageio_done()` for pageio parent buffers or frees virtual-address parent buf.
- Returns fdb object to cache.
- Asserts no outstanding dispatch remains.

## Integration Points
- Kernel buffer cache: `buf_t`, `bioclone()`, `freerbuf()`, `bioinit()`.
- Page I/O: `pageio_setup()`, `pageio_done()`, `pagezero()`, page list traversal.
- VM/physical I/O: `B_PHYS`, `B_SHADOW`, process pointer, shadow page lists.
- Completion callbacks through `fdb_iodone_t`.

## Risks and Subtle Areas
- Async state machine depends on `fd_iodispatch`, `FDB_DONE`, `FDB_ERROR`, `FDB_ASYNC`, and `FDB_ICALLBACK` combinations.
- `fdb_zero_holes()` page offset logic has an in-code warning about offset interpretation; callers must pass buffer-relative holes consistently.
- Parent buf is created once using the first requested len/flags; later clones reuse it.
- `fdb_add_hole()` updates `fd_iocount`, so holes are counted as accounted I/O even without a device request.
- Callback can receive either a completing `buf_t *` or `NULL` depending on path.

## Testing/Validation Signals
- Sync and async page I/O subrange clones.
- Virtual-address I/O with and without shadow page list.
- Hole insertion ordering and zeroing for page and virtual buffers.
- Error completion with residual accounting.
- Immediate callback versus final callback behavior.
