# sources/test-tools/liburing/test/rsrc_tags.c

Purpose: tests resource tags for registered files and buffers, including tag CQE emission on update/removal, no-CQE behavior for zero tags, empty buffer semantics, and partial registration failure cleanup.

Important APIs/types/functions: raw `__sys_io_uring_register`, `IORING_REGISTER_FILES2`, `IORING_REGISTER_BUFFERS2`, `IORING_REGISTER_FILES_UPDATE2`, `IORING_REGISTER_BUFFERS_UPDATE`, `io_uring_rsrc_register`, `io_uring_rsrc_update2`, `IORING_FEAT_RSRC_TAGS`, `io_uring_register_files_update`, fixed-buffer reads, and `io_uring_register_*_tags`.

Control flow: `has_rsrc_update()` gates feature support. `test_tags_generic()` registers resources with tags, updates tags, and verifies emitted CQEs carry old tags only when appropriate. `test_files()` covers file removal and disallowed nonzero tag on removal. `test_buffers_update()` ensures updating an in-use buffer delays tag CQE until the read finishes. `test_buffers_empty_buffers()` covers empty-to-full, full-to-empty, invalid empty length, and failed fixed reads on empty slots. `test_tagged_register_partial_fail()` ensures failed tagged registration does not emit stray CQEs.

State/persistence behavior: state lives in registered resource tables, tags, pipe fds, and CQEs. No durable files are created.

Dependencies/integration: uses raw registration ABI intentionally instead of wrappers for ABI coverage. Runs under default, IOPOLL, SQPOLL, and defer-taskrun modes where supported.

Risks/test signals: failures include missing or extra tag CQEs, wrong `user_data` tag values, premature update notification while buffers are still in use, or acceptance of invalid empty-buffer/tag combinations.
