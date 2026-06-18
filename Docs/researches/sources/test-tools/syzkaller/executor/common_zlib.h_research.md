# sources/test-tools/syzkaller/executor/common_zlib.h

Purpose: Small in-tree deflate/zlib inflater used by executor/csource code to expand compressed blobs into files without linking an external zlib.

Important APIs and control flow: the puff-derived implementation centers on `puff_state`, `puff_bits`, `puff_stored`, `puff_huffman`, `puff_decode`, `puff_construct`, `puff_codes`, `puff_fixed`, `puff_dynamic`, and `puff`. `puff` reads final-block/type bits, dispatches stored/fixed/dynamic blocks, and returns positive errors for short input/output, zero for success, and negative errors for malformed streams. `puff_zlib_to_file` skips the two-byte zlib header, mmaps a 132 MiB destination buffer, inflates into it, writes it to `dest_fd`, and unmaps it.

State and dependencies: most temporary tables are stack allocations; fixed Huffman tables are static and lazily initialized by `puff_fixed`, which is not explicitly thread-safe. `setjmp`/`longjmp` handles input exhaustion from bit readers. The wrapper depends on `mmap`, `munmap`, `write`, and `errno`.

Integration points: used by syzkaller pseudo-syscalls that materialize compressed images/files. The 132 MiB maximum is shared with `pkg/image/compression.go`.

Risks and tests: this altered puff variant only writes nonzero literal/copy bytes, preserving sparse zero-filled output from the mmap. That is intentional for sparse payloads but would be surprising for a general inflater. Static initialization races are possible if multiple executor threads first enter fixed-code inflation concurrently. Error translation uses `errno = -err`, which creates synthetic errno values for deflate errors. Test coverage is primarily through generated image/file execution paths rather than local unit tests in this subset.
