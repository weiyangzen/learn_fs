# sources/test-tools/fio/verify.c

Purpose: core fio data verification implementation. It generates verify patterns/checksum headers for writes, verifies read data against headers/patterns/zeroed trim results, offloads verification to async threads, and saves/loads verify state for offline or interrupted verification.

Important APIs/functions: exported entry points include `fill_buffer_pattern()`, `fill_verify_pattern()`, `populate_verify_io_u()`, `get_next_verify()`, `verify_io_u()`, `verify_io_u_async()`, `fio_verify_init()`, `verify_async_init()/exit()`, `paste_blockoff()`, `get_all_io_list()`, `verify_save_state()/load_state()/assign_state()/free_state()`, and verify-state skip/stop helpers. Internal checksum handlers cover MD5, CRC7/16/32/32C/64, SHA1, SHA256, SHA512, SHA3 variants, XXHASH, header-only, pattern, pattern-no-header, zero verification, and trimmed-zero verification.

Control flow: write preparation calls `populate_verify_io_u()`, which fills data and places headers at each verify interval. Read verification skips null/fake/device-verified cases, handles trimmed/zeroed flags, then walks every verify interval, validates the common header, selects the verify type, computes checksum or pattern comparison, logs detailed failures, and optionally dumps received/expected buffers. Async mode queues `io_u`s on `td->verify_list`; detached verifier threads drain lists, call `verify_io_u()`, update nonfatal errors, and signal exit.

State/persistence: mutates `io_u` flags, file refs, verify queues, `td->io_hist_tree/list`, `td->io_hist_len`, RNG seeds, async thread counters, and failure counts. Persistent verify-state files are named by `verify_state_gen_name()`, written with `O_SYNC`, include header CRC/version/size, and serialize inflight plus failed `numberio` values. Dump files may be written under `aux_path` on verify failures.

Dependencies/integration: deeply coupled to fio thread/job options, IO history, trim, file lifecycle, CRC/hash libraries, random/pattern helpers, pthreads, endian helpers, and global thread iteration macros.

Risks/test signals: high-risk areas are header-size vs block-size validation, `verify_offset` header swaps, async pattern formatting with offset placeholders, `np` not applicable here but C buffer bounds, failure dump filenames, detached-thread shutdown, and verify-state compatibility. Strong tests should cover every verify type, partial intervals, trim-zero reads, verify-fatal termination, fsynced policy thresholds, failed-numberio skip, corrupted state CRC, and cross-version header rejection.
