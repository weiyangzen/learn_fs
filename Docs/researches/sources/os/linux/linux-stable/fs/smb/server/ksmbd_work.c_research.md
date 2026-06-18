# File Research: sources/os/linux/linux-stable/fs/smb/server/ksmbd_work.c

Read status: complete.

## Purpose
Allocates, frees, queues, and prepares per-request `ksmbd_work` objects and response iovec arrays.

## Main Responsibilities
- Create/destroy the slab cache for `ksmbd_work`.
- Create/destroy the per-CPU ksmbd I/O workqueue.
- Allocate work objects with default compound FIDs, list heads, aux-read list, and initial kvec array.
- Free response/request buffers, transform buffers, aux read buffers, async IDs, and kvec storage.
- Queue work to `ksmbd-io`.
- Pin response buffers and optional read auxiliary buffers into kvecs while updating RFC1001 length.
- Allocate interim response buffers.

## Dependencies And Role
Used by SMB request dispatch and response construction. Integrates with connection async IDAs and RFC1002 framing helpers.

## Risks
Response iovec growth and RFC1001 length accounting are central to correct replies. Aux-read ownership and async ID release must stay aligned with all error paths.
