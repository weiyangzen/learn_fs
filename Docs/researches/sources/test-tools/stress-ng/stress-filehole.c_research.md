# sources/test-tools/stress-ng/stress-filehole.c

Purpose: implements `filehole`, a sparse-file stressor that repeatedly writes, mmaps, zeroes, punches holes, probes holes/data with `lseek()`, and optionally defragments the file.

Important APIs/types/functions: `fallocate_modes[]` weights punching holes three-to-one over zero-range when available. `stress_filehole_write()` and `stress_filehole_read()` provide positioned I/O wrappers with expected transient-error handling. `stress_filehole_io()` writes a page, validates mmap visibility, modifies the mmap, applies a random fallocate mode, optionally verifies zeroed data, writes neighboring data, and applies a second zero/hole operation. `stress_filehole_lseek_read()` samples `SEEK_SET`, `SEEK_DATA`, and `SEEK_HOLE`; `stress_filehole_non_zeros_to_holes()` converts nonzero pages to holes; `stress_filehole_defrag()` rewrites the sparse file into a dense temporary copy and renames it.

Control flow: the stressor clamps `--filehole-bytes`, allocates two page-sized buffers, creates a temp file, synchronizes, and loops. Each pass clears or truncates the file, writes and fallocates in reverse order, random order, and forward order, gathers max size/block and extent metrics, does random hole/data reads, fills with random data, punches alternating gaps, optionally defragments, converts nonzero pages back to holes, and repeats.

State and persistence behavior: creates a temporary file path and page buffers. File contents, extents, blocks, and sparse layout are heavily mutated but removed on cleanup. Metrics preserve maximum file size, maximum blocks, and average extents per file for the run.

Dependencies and integration points: compiled only with `fallocate()` plus punch-hole or zero-range support. Uses stress-ng mmap, madvise, fs extent, temp-file, fadvise, and metrics helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS`, optional verification.

Risks: sparse behavior is filesystem-specific. ENOSPC/EFBIG/EAGAIN/EINTR are skipped, while other I/O errors fail. The fallback branch in `stress_filehole_non_zeros_to_holes()` contains unreachable typo-like references hidden by compile guards, so feature macro changes should be cautious. Defrag rename failure is nonfatal and silently keeps the original file.

Test signals: run with and without `--verify`, with minimum and large `--filehole-bytes`, and with `--filehole-defrag`. Confirm extents/block metrics are emitted, zero verification does not fail on punch/zero modes, and cleanup removes both original and `-tmp` files.
