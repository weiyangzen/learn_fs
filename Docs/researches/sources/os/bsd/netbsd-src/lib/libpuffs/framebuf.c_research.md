# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/framebuf.c

This file implements libpuffs frame buffers and frame-vector I/O scheduling. A `puffs_framebuf` stores callback or call-context continuation state, an expandable byte buffer, cursor/max offsets, completion errno, internal state flags, and queue links. Basic APIs allocate, destroy, recycle, duplicate, reserve space, put/get data at current or explicit offsets, seek, expose windows, and return the raw data pointer.

The enqueue APIs place buffers on per-fd send queues in blocking call-context mode, callback mode, just-send mode, direct receive, direct send, or event-wait mode. Blocking APIs mark buffers non-destroyable while queued and yield the current call context until completion. Error notification resumes a context, calls a callback, or destroys the frame.

`puffs__framev_input` reads frames via a supplied frame controller, matches responses to outstanding request buffers with `cmpfb`, moves buffer ownership from internal read buffers to app buffers, calls `gotfb` for unsolicited frames, and resumes contexts/callbacks. `puffs__framev_output` writes queued frames, moves reply-waiting frames to the response queue, destroys no-reply frames, or resumes direct senders. The file also manages kqueue registration, fd enable/disable, read/write close notification, fd removal, and frame-controller initialization/exit.

Risks are high due to queued ownership flags, partial I/O, response matching, direct-buffer paths, context resumption during list iteration, and fd close races.
