# sources/test-tools/fio/engines/nbd.c

## Purpose
Implements an asynchronous Network Block Device engine using libnbd. It connects to an NBD URI, discovers export size, issues asynchronous read/write/trim/flush commands, polls for command completion, and maps callbacks back to fio `io_u` objects.

## Important APIs, Types, And Functions
`struct nbd_data` stores the libnbd handle, debug flag, dynamically sized completed-`io_u` list, and completion count. `struct nbd_options` stores the required URI. Key functions are `nbd_setup()`, `nbd_init()`, `nbd_queue()`, `cmd_completed()`, `retire_commands()`, `nbd_getevents()`, `nbd_event()`, and `nbd_cleanup()`.

## Control Flow
`setup` creates fio's synthetic file if needed, creates an NBD handle, connects synchronously to fetch size, records `real_file_size`, then closes the setup handle. `init` creates a per-thread handle and connects. `queue` attaches `nbd_data` to `io_u->engine_data`, asserts read/write size is within `NBD_MAX_REQUEST_SIZE`, and calls the appropriate `nbd_aio_*` function with a callback. The callback stores the error result and appends the `io_u` to `completed` via `realloc()`. `getevents` repeatedly calls `nbd_poll()` and retires completed cookies until enough completions exist. `event` pops completed `io_u` entries in LIFO order.

## State And Persistence
The network export is persistent; fio file state is synthetic. Completion state is held in a heap array on `nbd_data`. The libnbd handle is per fio thread after init.

## Dependencies And Integration Points
Depends on libnbd, fio diskless/noextend engine behavior, and fio async event callbacks. It provides no generic file open because the connection is the target.

## Risks
Setup error paths can return without freeing partially allocated `nbd_data` or handles. Completion list grows with `realloc()` and is popped LIFO, ignoring the event index. Timeout handling notes that loop iterations can wait longer than requested. `max` is not used to cap event return count. The read/write request limit is an assert, not a recoverable validation.

## Test Signals
Test missing/bad URI, size discovery, reconnect in `init`, read/write/trim/flush, callback error propagation with and without errno, debug logging, request sizes near 64 MiB, timeout behavior, multiple completions, and cleanup after setup/init failures.
