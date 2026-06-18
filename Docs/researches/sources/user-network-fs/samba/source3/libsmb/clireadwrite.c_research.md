# sources/user-network-fs/samba/source3/libsmb/clireadwrite.c

## Purpose

This file implements SMB client file read, write, full-write, pull, push, and splice helpers. It handles SMB1 read/write-andx framing, SMB2 helper dispatch, max transfer sizing, credit/request availability, ordered parallel chunk pipelines, and fallback copy loops.

## Important APIs, Types, and Functions

Important APIs are `cli_read_andx_create/send/recv`, `cli_pull_send/recv`, `cli_pull()`, `cli_read_send/recv`, `cli_read()`, `cli_write_andx_create/send/recv`, `cli_write_send/recv`, `cli_writeall_send/recv`, `cli_writeall()`, `cli_push_send/recv`, `cli_push()`, and `cli_splice()`. Internal sizing helpers are `cli_read_max_bufsize()` and `cli_write_max_bufsize()`. Chunk state structs keep offsets, buffers, partial sizes, outstanding subrequests, and ordered linked lists.

## Control Flow

SMB1 read/write create functions construct `SMBreadX`/`SMBwriteX` word vectors, submit chains, and validate returned byte counts and offsets. Single-read/write APIs choose SMB2 or SMB1 based on dialect and respect available credits or SMB1 request slots. `cli_pull_send()` and `cli_push_send()` compute chunk sizes and a window of up to 256 chunks, issue chunks only when request slots are available, and preserve ordered sink delivery for reads. `cli_writeall()` loops partial SMB1 writes until the requested size is written. `cli_splice()` prefers SMB2 server-side copy when source and destination are the same SMB2 connection, falling back to 1 MiB read/write blocks.

## State and Persistence Behavior

Reads are remote-state neutral. Writes, writeall, push, and splice persist data changes on remote files. Local state is request-scoped: buffers may be held under subrequest talloc ownership for full chunks, copied into chunk buffers for partial reads, and freed as chunks complete.

## Dependencies and Integration Points

The file depends on SMB1 low-level request building, SMB2 read/write/splice helpers, connection capability flags, signing/encryption status, `cli_state_available_size()`, tevent, and DLIST macros. It is the core data path used by client file copy, get/put, and higher-level libsmb operations.

## Risks and Test Signals

Risks include trusting server byte counts, large-offset handling without `CAP_LARGE_FILES`, short reads/writes, zero-byte writes, credit starvation, preserving read order under parallel completion, overflow in offset advancement, and fallback cancellation. Tests should cover SMB1/SMB2 reads and writes across max chunk boundaries, signing/encryption reduced sizes, EOF as zero bytes, server over-read/over-write responses, partial writes, push source EOF, splice fallback after unsupported SMB2 copychunk, and active-async rejection in sync wrappers.
