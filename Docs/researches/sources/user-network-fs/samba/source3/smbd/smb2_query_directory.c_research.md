# sources/user-network-fs/samba/source3/smbd/smb2_query_directory.c

## Purpose
This file implements SMB2 QUERY_DIRECTORY handling. It parses the SMB2 request, validates file ids and buffer sizes, maps SMB2 find information classes to source3 directory enumeration levels, maintains per-handle directory pointer state, marshals directory entries, and optionally fetches DOS mode and creation time asynchronously.

## Important APIs, Types, And Functions
The request entry point is `smbd_smb2_request_process_query_directory()`. The async implementation is `smbd_smb2_query_directory_send()`/`recv()` with state in `struct smbd_smb2_query_directory_state`. Enumeration is driven by `smb2_query_directory_next_entry()`, which calls `smbd_dirptr_lanman2_entry()`. Async DOS mode support uses `fetch_dos_mode_send()`/`recv()`, `dos_mode_at_send()`, `dos_mode_at_recv()`, and callbacks `smb2_query_directory_dos_mode_done()` and `fetch_dos_mode_done()`.

## Control Flow
The top-level parser verifies a 0x21-byte body, input name offset/length, minimum output buffer size, UTF-16 to Unix conversion, NUL safety, credit charge, and fsp lookup. The send path rejects non-directory handles, empty or slash-containing masks, shadow-copy timestamp masks, oversized buffers, unsupported find classes, and POSIX information on non-POSIX handles. It can reopen a directory for `SMB2_CONTINUE_FLAG_REOPEN`, canonicalizes non-wildcard last components, creates or rewinds `fsp->dptr`, allocates an output buffer with a safety margin, applies `dont descend`, configures async DOS mode, then loops entries until full, single-entry, no-more-files, async backpressure, or injected delay. The done path emits an 8-byte SMB2 body plus the dynamic output buffer.

## State And Persistence
Enumeration state persists on the open directory handle via `fsp->dptr`; subsequent calls distinguish first empty status `NT_STATUS_NO_SUCH_FILE` from later `STATUS_NO_MORE_FILES`. The tevent request tracks output buffer pointers, last entry offset, async DOS-mode job count, `max_count`, and delay state. No durable disk state is modified.

## Dependencies And Integration Points
This code integrates SMB2 request framing, file-id lookup, source3 directory pointer APIs, wildcard/case handling, `dont descend` share configuration, trans2 find marshalling, POSIX directory handles, pthreadpool-backed DOS mode lookup, per-thread CWD support, VFS stat/create-time helpers, and SMB2 async internal request marking.

## Risks And Test Signals
Tests should cover all supported find classes, invalid info class, POSIX find class gating, restart/single/reopen flags, empty first scan versus exhausted later scan, wildcard and case-preserved masks, illegal UTF-16 and embedded NUL names, shadow-copy timestamp masks, client max-trans violations, credit-charge failures, async DOS-mode completion ordering, DFS-link DOS mode preservation, and delay injection. Key risks are output buffer overrun/truncation, wrong last-entry next offset, leaked `smb_fname` during async mode, incorrect status mapping when the buffer is too small, and request lifetime while async jobs are attached to an fsp.
