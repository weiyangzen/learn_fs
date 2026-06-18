# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsp.c

Implements Ghostscript’s callback-based `display` device for embedding GS in applications. It wraps a memory device, renders into a caller-visible bitmap, and calls host callbacks for open, presize, size, update, sync, page, preclose, close, memory allocation, and separation metadata.

Key behavior:
- Supports many packed display formats via `DisplayFormat`: native 1/4/8/16-bit, gray, RGB/BGR, CMYK, and DeviceN separations.
- Parses `DisplayHandle` as string on 64-bit systems and legacy long on 32-bit systems.
- Allows resize while open, but rejects changing handle/format after open.
- Allocates backing bitmap either through callback `display_memalloc/display_memfree` or Ghostscript non-GC memory.
- Uses `gdev_mem_device_for_bits`, `gs_make_mem_device`, and forwards draw ops to the memory device.
- DeviceN separation support maps spot components and equivalent CMYK values through `display_separation`.

Risks / notes:
- Host callback ABI is trusted after structure validation; incorrect callback behavior can break rendering.
- Pointer encoded in `DisplayHandle` is inherently unsafe if exposed to untrusted PostScript.
- Row-size arithmetic uses `int`; very large dimensions could overflow in old environments.
