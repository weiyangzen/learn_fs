# File Research: sources/virtualization/spdk/lib/util/pipe.c

This file implements a single-buffer circular pipe with iovec-based reader/writer access and optional shared buffer grouping.

`spdk_pipe_create()` wraps a caller-provided buffer and size in a pipe object. `spdk_pipe_destroy()` removes the pipe from any group, returns the underlying buffer pointer, and frees the pipe object.

Writer APIs expose writable space without copying. `spdk_pipe_writer_get_buffer()` returns up to two iovecs for the current free range, wrapping at the end of the buffer when needed. If the pipe is full or the request is zero, it returns an empty first iovec. `spdk_pipe_writer_advance()` validates the requested advance fits in free space, moves the write pointer, wraps if needed, and marks the pipe full when write catches read.

Reader APIs mirror this. `spdk_pipe_reader_bytes_available()` computes readable bytes. `spdk_pipe_reader_get_buffer()` returns up to two readable iovecs. `spdk_pipe_reader_advance()` validates the read advance, clears `full`, resets both pointers to zero when empty, and, if the pipe belongs to a group, returns its buffer to the group and sets `pipe->buf` null.

Pipe groups let empty pipes share buffers of matching size. `spdk_pipe_group_create()` and destroy manage a list of free buffers. `spdk_pipe_group_add()` associates a pipe with a group and immediately releases its buffer if the pipe is empty. `spdk_pipe_group_remove()` reacquires a matching buffer before disassociating the pipe.

The implementation assumes single-threaded or externally synchronized access. Group buffers are stored by casting the start of the pipe buffer to `struct spdk_pipe_buf`, so grouped buffers must be large/aligned enough to hold that header when idle.
