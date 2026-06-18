# File Research: sources/virtualization/guestfs-tools/builder/pxzcat-c.c

## Scope

OCaml C stub implementing virt-builder decompression of xz templates, with optional parallel liblzma support and fallback to external `xzcat`.

## Public OCaml Stubs

- `virt_builder_using_parallel_xzcat` reports whether parallel liblzma support was compiled in.
- `virt_builder_pxzcat` decompresses an input xz file into an output file.

## Fallback Behavior

- Opens/truncates the output file, forks, redirects child stdout to the output, and execs configured `XZCAT`.
- Parent waits and raises OCaml failure if `xzcat` exits abnormally or nonzero.

## Parallel Behavior

- Enabled only when liblzma and needed index APIs are available.
- Determines thread count from online CPUs.
- Validates xz header magic.
- Parses xz stream indexes backward from the file end, handling stream padding, stream headers/footers, and combined multi-stream indexes.
- Preallocates output to the total uncompressed size, using careful truncation/write sequencing to avoid ext4 `auto_da_alloc` flush behavior.
- Iterates xz blocks across worker threads. A mutex protects the shared `lzma_index_iter`; workers use `pread`/`pwrite` to avoid shared file offset races.
- Each worker decodes block headers, verifies compressed size against the index, decompresses block data, and writes nonzero output buffers to preserve sparseness.

## Dependencies And Risks

- Uses OCaml exception APIs from C; error paths may not return normally.
- Thread workers return status pointers in per-thread state and aggregate failures after joins.
- Parallel path depends on correct xz indexes; corrupt footer/header/index data becomes OCaml invalid-argument errors.
- Sparse preservation depends on `is_zero` checks before `pwrite`.
