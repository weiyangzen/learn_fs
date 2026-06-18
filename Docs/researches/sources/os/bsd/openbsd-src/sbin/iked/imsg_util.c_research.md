# File Research: sources/os/bsd/openbsd-src/sbin/iked/imsg_util.c

Read completely: 122 lines.

Provides small internal convenience wrappers around OpenBSD's `imsg`/`ibuf` API for iked message buffers.

Functions:
- `ibuf_new()` creates a dynamic `ibuf` capped at `IKED_MSGBUF_MAX`, optionally fills it with zero bytes when `data == NULL`, or copies caller data into it.
- `ibuf_static()` opens a fixed-size `IKED_MSGBUF_MAX` buffer for incremental message construction.
- `ibuf_length()` safely returns `0` for `NULL` or `ibuf_size()` otherwise.
- `ibuf_getdata()` extracts a nested/leading `ibuf` of a requested length and returns an owned dynamic copy.
- `ibuf_dup()` duplicates an existing `ibuf` into a new owned buffer.
- `ibuf_random()` opens a buffer, reserves the requested length, and fills it with `arc4random_buf()`.
- `ibuf_setsize()` truncates/sets the write position if the requested length is not beyond the allocated buffer size.

Risks and notes:
- `ibuf_setsize()` directly updates `buf->wpos`, so callers must pass a valid mutable `ibuf`.
- Allocation/copy failures consistently free partial buffers and return `NULL` or `-1`.
