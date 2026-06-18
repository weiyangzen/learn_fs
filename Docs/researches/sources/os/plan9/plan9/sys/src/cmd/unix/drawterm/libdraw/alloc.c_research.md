# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/alloc.c

Implements client-side `Image` allocation, lookup by devdraw name, naming, and freeing for drawterm’s libdraw interface. It serializes draw protocol messages (`b`, `n`, `N`, `f`) into the display buffer with `bufimage`, `BPLONG`, and `flushimage`.

Key functions:
- `allocimage` and `_allocimage`: validate channel descriptors, allocate a server-side image id, send allocation metadata, create or initialize an `Image`.
- `namedimage`: requests an existing named devdraw image and reads its geometry/channel metadata from `ctlfd`.
- `nameimage`: binds or unbinds an image name in devdraw.
- `_freeimage1` and `freeimage`: send free messages and unlink window images from the display window list.

Important behavior:
- Replicated images receive a huge finite clipping rectangle to avoid overflow while behaving practically infinite.
- Allocation failures after server-side creation attempt to send an `f` free message to avoid leaking server resources.
- Channel parsing depends on `chantodepth` and `strtochan` from libdraw channel helpers.
