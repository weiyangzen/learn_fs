# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/vncs.h

This server-side VNC header defines `Rlist` and `Vncs`, extending the common `Vnc` state with server-specific per-client state.

Key structures:
- `Rlist` tracks dirty rectangles using a bounding box, allocation size, count, and rectangle array.
- `Vncs` embeds `Vnc`, then adds linked-list membership, remote/netpath strings, encoding callbacks, encoding feature flags, mouse-warp state, update request state, rectangle list, process-exit accounting, cursor/snarf versions, and a per-client translated `Memimage`.

Important fields:
- `countrect` and `sendrect` select the active framebuffer encoding implementation.
- `copyrect`, `canwarp`, `needwarp`, and `warppt` track optional client capabilities.
- `updaterequest` controls whether writer loop should emit a frame update.
- `ndead` and `nproc` ensure shared client resources are freed only after all per-client processes exit.
- `imagechan` records the Plan 9 channel corresponding to the client-requested VNC pixel format.

Declared external implementations:
- Encoding count/send functions for raw, RRE, CoRRE, and hextile.
- Rectangle-list helpers `addtorlist` and `freerlist`.

Role:
- This header is the private contract between `vncs.c`, rectangle-list management, and rectangle encoders.
