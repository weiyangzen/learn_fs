# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/requests.c

This file implements the default puffs filesystem frame controller for communication with the kernel-side provider. Frames are carried with a `struct putter_hdr` prefix and puffs request data.

`puffs__fsframe_read` incrementally reads from the fd into a `puffs_framebuf`. It first ensures enough bytes for the `putter_hdr`, then reads the remaining `pth_framelen` bytes. It grows the frame buffer window as needed, treats EOF as `ECONNRESET`, treats `EAGAIN` as incomplete but not fatal, and rewinds the frame buffer to offset zero when a full frame has arrived.

`puffs__fsframe_write` finalizes the frame length before the first write by mapping the leading `struct puffs_req` and setting `preq_pth.pth_framelen` to `preq_buflen`. It then writes until the full frame length is sent or the fd would block, again returning `ECONNRESET` for zero-byte writes and preserving partial progress via the frame buffer offset.

`puffs__fsframe_cmp` decides whether an incoming frame is a response to a previously sent frame. It maps both puffs request headers, rejects non-response frames by setting `*notresp`, and otherwise compares request ids. `puffs__fsframe_gotframe` rewinds a completed frame and hands it to `puffs__ml_dispatch`.
