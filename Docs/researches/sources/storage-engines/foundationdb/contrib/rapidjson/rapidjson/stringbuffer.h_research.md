# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/stringbuffer.h

## Purpose

`stringbuffer.h` implements RapidJSON's in-memory output stream. `GenericStringBuffer` is the usual sink for `Writer`, schema diagnostics, and any API that needs generated JSON or pointer text as a contiguous string.

## Important APIs and Types

`GenericStringBuffer<Encoding, Allocator>` exposes stream-compatible `Put`, `PutUnsafe`, and `Flush`, buffer management methods `Clear`, `ShrinkToFit`, `Reserve`, `Push`, `PushUnsafe`, and `Pop`, plus `GetString` and `GetSize`. `StringBuffer` aliases UTF-8 with `CrtAllocator`. The header specializes `PutReserve`, `PutUnsafe`, and `PutN<StringBuffer>` so writer hot paths can reserve stack space and use `memset` for repeated UTF-8 chars.

## Control Flow

Writes push characters into an `internal::Stack`. `GetString` temporarily pushes a null terminator, immediately pops it, and returns the stack bottom pointer, giving callers a null-terminated view without changing logical size. `ShrinkToFit` uses the same temporary terminator trick before compacting. Move construction and assignment transfer the underlying stack when C++11 rvalue references are available.

## State and Persistence

The buffer owns an `internal::Stack<Allocator>` and optionally uses a caller-supplied allocator. Data remains in memory until `Clear`, destruction, or stack reallocation. Returned `GetString` pointers are invalidated by later mutations or reallocations. Copy construction and assignment are intentionally disabled.

## Dependencies and Integration Points

The header depends on `stream.h` and `internal/stack.h`. `writer.h` includes it for the common `Writer<StringBuffer>` specialization, and schema verbose diagnostics can stringify pointers through `GenericStringBuffer`.

## Risks and Edge Cases

`GetString` on an empty buffer depends on stack bottom behavior after the temporary push/pop. `GetSize` reports bytes in the internal stack, not character count for wide encodings. `PutUnsafe` and `PushUnsafe` require prior reservation and can overrun if used incorrectly by custom code. Pointer stability is only guaranteed until the next mutating operation.

## Test Signals

Tests should cover writing and reading null-terminated output, clearing and reusing buffers, reserve/push/pop behavior, shrink-to-fit preserving content, move semantics where enabled, writer integration, and `PutN` specialization for repeated UTF-8 characters.
