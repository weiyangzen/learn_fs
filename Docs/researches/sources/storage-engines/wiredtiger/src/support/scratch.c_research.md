# sources/storage-engines/wiredtiger/src/support/scratch.c

## Purpose
`scratch.c` implements general `WT_ITEM` buffer growth/formatting helpers and per-session scratch-buffer caching. It provides reusable temporary buffers for internal code, printable byte/string formatting, byte-size formatting, and extension scratch allocation/free wrappers.

## Important APIs, Types, and Functions
Buffer helpers include `__wt_buf_grow_worker`, `__wt_buf_fmt`, `__wt_buf_catfmt`, `__wt_buf_set_printable`, `__wt_buf_set_printable_format`, and `__wt_buf_set_size`. Scratch lifecycle APIs include `__wt_scr_alloc_func`, `__wt_scr_discard`, `__wt_ext_scr_alloc`, and `__wt_ext_scr_free`. Diagnostic builds track allocation function and line in `session->scratch_track`.

## Control Flow
`__wt_buf_grow_worker` handles three cases: empty buffers, data already inside `buf->mem`, and data outside the buffer that must be copied local. Formatting helpers grow buffers through the common varargs buffer-format macros. Printable-format conversion tries schema-aware pack unpacking, then falls back to raw printable bytes if the byte string does not match the format. Scratch allocation optionally locks internal sessions, scans for the best free buffer or empty slot, grows the scratch pointer array in chunks of ten when needed, initializes or grows the chosen buffer, marks it in use, and returns it. Discard reports any still-in-use scratch buffers before freeing all scratch memory.

## State and Persistence Behavior
Scratch state lives on `WT_SESSION_IMPL`: `scratch`, `scratch_alloc`, `scratch_cached`, `scratch_lock`, and diagnostic `scratch_track`. Buffers are cached in memory for reuse and freed when the session discards scratch buffers. Extension scratch allocation returns raw `mem` pointers backed by session scratch `WT_ITEM`s.

## Dependencies and Integration Points
The file depends on WiredTiger allocation/reallocation, buffer initialization/free, varargs formatting macros, raw hex helpers, pack/unpack helpers, session flags, spin locks for shared internal sessions, extension API types, and diagnostic logging. It is a broad support dependency because many subsystems need temporary buffers.

## Risks
Scratch buffers are single-owner while marked `WT_ITEM_INUSE`; failure to free them is reported at session discard and can inflate per-session memory. Internal sessions need `scratch_lock` because they may be shared across threads. Extension free searches by raw memory pointer and logs an error for unknown pointers; callers must return exactly the pointer from `__wt_ext_scr_alloc`. `__wt_buf_grow_worker` must preserve `data` offsets correctly for overflow-item buffers where `data` points inside `mem` after a header. Formatted append asserts that existing data is local to the buffer.

## Test Signals
Tests should cover grow with null data, local offset data, external data copy, append formatting, printable fallback after format mismatch, exact and approximate byte-size formatting, scratch reuse choosing the best-sized free buffer, scratch array growth, diagnostic leak reporting, internal-session concurrent scratch allocation, extension alloc/free with default session fallback, and freeing an unknown extension pointer.
