<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/verify_build.h -->
# Research: sources/storage-engines/wiredtiger/src/include/verify_build.h

## Purpose

`verify_build.h` is a compile-time contract header. It stops the build when the compiler, platform ABI, or struct definitions no longer satisfy layout assumptions that WiredTiger depends on for public/private object aliasing, block metadata encoding, cache-line padding, update-record layout, and fixed-size file offsets.

The file has no runtime functions. Its entire behavioral surface is `static_assert` plus the `WT_VERIFY_OPAQUE_POINTER` macro used near API entry points to prove that internal structures begin with their public `iface` field.

## Important APIs, Types, and Macros

`WT_VERIFY_OPAQUE_POINTER(type)` expands to a `static_assert(offsetof(type, iface) == 0, ...)`. WiredTiger exposes public handles as opaque pointers whose first field is the public interface object. Internal code casts between public and private types, so `iface` must be the first member.

The fixed-size assertions check `sizeof(WT_BLOCK_DESC) == WT_BLOCK_DESC_SIZE` and `sizeof(WT_REF) == WT_REF_SIZE`. Those constants encode expected packed layout for storage-engine metadata and btree reference structures.

The `WT_BLOCK_DISAGG` assertions pin offsets for the shared prefix with `WT_BLOCK`: `name`, `objectid`, `ref`, `q`, and `hashq`. The comment explains that both structures can be inserted into `conn->blockhash` / `conn->blockqh` and traversed as `WT_BLOCK *`, so prefix aliasing must remain exact.

The `WT_UPDATE` checks assert that the whole update structure aligns to an 8-byte boundary, that its variable-length `data` field starts at `WT_UPDATE_SIZE`, and that `WT_UPDATE_SIZE_NOVALUE` currently equals `sizeof(WT_UPDATE)` with no extra difference from `WT_UPDATE_SIZE`.

`WT_PADDING_CHECK(s)` asserts either the structure is no larger than one cache line or its size is a multiple of `WT_CACHE_LINE_ALIGNMENT`. It is applied to `WT_TXN_SHARED`, making cache-line padding a build-time invariant.

The platform assertions require `sizeof(size_t) >= 8`, `sizeof(wt_off_t) == 8`, and `sizeof(time_t) <= sizeof(uint64_t)`.

## Control Flow

This header runs at compile time. Including it after the relevant type definitions causes the compiler to evaluate all `static_assert` expressions. Success produces no code. Failure aborts compilation with the specific assertion message.

`WT_VERIFY_OPAQUE_POINTER` is a macro rather than a global assertion because it is invoked at relevant API implementation points, for example connection open, session API code, log cursor code, and cursor implementations. These invocations localize the guarantee to the internal handle type being exposed through a public interface.

## State and Persistence Behavior

There is no runtime state, persistent state, or emitted data. The header protects the representation of structures that are persisted or shared elsewhere. `WT_BLOCK_DESC` relates to block metadata, `WT_UPDATE` contains inline variable-length update data, `WT_REF` participates in btree state, and `wt_off_t` controls on-disk addressability. If these layouts drift, persisted data interpretation or pointer casting could become unsafe; the header prevents that at build time.

## Dependencies and Integration Points

The header depends on `assert.h` for `static_assert` availability and on prior declarations of all checked WiredTiger types and constants: `WT_BLOCK_DESC`, `WT_BLOCK_DESC_SIZE`, `WT_REF`, `WT_REF_SIZE`, `WT_BLOCK_DISAGG`, `WT_BLOCK`, `WT_UPDATE`, `WT_UPDATE_SIZE`, `WT_UPDATE_SIZE_NOVALUE`, `WT_TXN_SHARED`, `WT_CACHE_LINE_ALIGNMENT`, `wt_off_t`, and alignment helpers such as `WT_ALIGN`.

It integrates with the public API object model. `WT_VERIFY_OPAQUE_POINTER` is used by internal implementations for `WT_CONNECTION_IMPL`, `WT_SESSION_IMPL`, and cursor subclasses such as backup, config, dump, file, layered, log, stat, table, data-source, and prepared-discovery cursors.

It also integrates with disaggregated storage through the `WT_BLOCK_DISAGG` / `WT_BLOCK` shared-prefix assertions. These checks document and enforce a deliberate aliasing relationship used by connection block hash and queue traversal code.

## Risks and Edge Cases

The assertions are intentionally strict. A legitimate struct layout change requires updating the corresponding size constants, offset assertions, and any code that serializes or aliases the structure. Treating a compile failure here as a nuisance would risk silent corruption or invalid pointer casts.

The `WT_BLOCK_DISAGG` prefix contract is especially sensitive because C permits the code to compile if fields drift, but traversal through `WT_BLOCK *` would read the wrong fields. These assertions are the main guard against that class of bug.

The `WT_UPDATE` checks encode assumptions about trailing padding and variable-length-array placement. Adding fields near `data`, changing timestamp types, or changing alignment rules can require a coordinated update to size macros and allocation logic.

Platform support is intentionally narrowed. Builds with 32-bit `size_t`, 4-byte file offsets, or unexpectedly large/non-integral `time_t` fail at compile time rather than producing a binary with untested address-cookie or time conversion behavior.

`WT_PADDING_CHECK` only checks size divisibility, not field-level false sharing. It is a coarse build signal; reviewers still need to inspect concurrent fields when changing shared structures.

## Test Signals

The primary test signal is compilation across supported compilers and build variants. Any failure in this file should be investigated as an ABI/layout change rather than bypassed.

Additional targeted signals include compiling with disaggregated storage enabled after edits to `WT_BLOCK` or `WT_BLOCK_DISAGG`, building cursor/API files after adding an `iface`-backed internal type, and running format or recovery tests after touching `WT_BLOCK_DESC`, `WT_REF`, `WT_UPDATE`, or `wt_off_t` definitions.

Static analysis or small compile-only tests can also verify that each internal public-handle type invokes `WT_VERIFY_OPAQUE_POINTER`, but the current repository mainly enforces this by explicit macro calls in the implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/verify_build.h -->
