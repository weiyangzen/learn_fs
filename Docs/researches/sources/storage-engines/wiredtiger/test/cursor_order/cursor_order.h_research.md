# sources/storage-engines/wiredtiger/test/cursor_order/cursor_order.h

## Purpose
This header defines shared types and function declarations for the cursor-order test.

## Important APIs, Types, and Functions
- Includes `test_util.h` and `<signal.h>`.
- Defines `FNAME "file:cursor_order.%03d"` for generated file URIs.
- Defines `enum __ftype { ROW, VAR }`.
- Defines `SHARED_CONFIG`, holding connection pointer, file type, key range, operation counts, thread counts, multiple-file/vary flags, and finish flag.
- Declares `load`, `ops_start`, and `verify`.

## Control Flow
The header has no executable control flow. It establishes the contract shared by the main driver, file loader/verifier, and operation workload implementation.

## State and Persistence Behavior
`SHARED_CONFIG` is the in-memory state container passed between modules. `key_range` tracks current append range; `thread_finish` signals worker shutdown; `conn` carries the active WiredTiger connection.

## Dependencies and Integration Points
It is included by `cursor_order.c`, `cursor_order_file.c`, and the operations source. The `FNAME` pattern aligns multiple-file workload naming across modules.

## Risks and Test Signals
Mismanaging shared fields can affect thread coordination and generated URI consistency. Since this is a header, direct test signals come from consumers.
