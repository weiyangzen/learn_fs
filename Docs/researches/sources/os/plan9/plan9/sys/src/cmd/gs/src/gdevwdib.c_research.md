# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevwdib.c

Implements the `mswindll` Microsoft Windows Ghostscript DLL display device using a DIB-style memory device backing store.

Key behavior:
- Defines a Windows DIB device that wraps a Ghostscript memory device, global-memory backing allocation, optional Win32 mutex, lock count, and 16-bit Windows segment bookkeeping when needed.
- `win_dib_open` performs common window setup, creates a mutex on non-Win32s Win32 systems, validates memory-device support for the selected depth, allocates the backing bitmap, and notifies the DLL callback of device creation and size.
- `win_dib_get_initial_matrix` uses a lower-left origin with positive Y scaling, unlike most display devices.
- `win_dib_close` locks the device during close notification, frees the bitmap, closes the mutex, and delegates common window close.
- Drawing operations forward fill, mono copy, and color copy into the wrapped memory device, splitting operations at 64K segment boundaries for 16-bit builds.
- `win_dib_get_bits` delegates scan-line readback to the memory device; `win_dib_put_params` locks the device while common Windows parameters are updated.
- Exports DLL APIs to copy the full DIB (`gsdll_copy_dib`), copy the palette (`gsdll_copy_palette`), draw a source rectangle to a caller-supplied HDC (`gsdll_draw`), lock/unlock the device (`gsdll_lock_device`), and expose bitmap header/palette/row pointers (`gsdll_get_bitmap_row`).
- `win_dib_repaint` builds a `BITMAPINFO` header and uses `SetDIBitsToDevice`, including 15-bit and 16-bit bitfield masks and chunking transfers above roughly 2 MB.
- `win_dib_make_dib` constructs a global-memory DIB copy for a requested rectangle, including bitmap header, RGB palette or bitfield masks, and padded scan-line data.
- `win_dib_alloc_bitmap` sizes the memory-device width to avoid segment crossings on 16-bit builds, allocates global memory for raster data and line pointers, aligns the base, initializes the memory device, and sends size notifications.
- `win_dib_free_bitmap` unlocks and frees the global backing allocation.
- `win_dib_lock_device` uses a mutex on modern Win32 or a counter on Win16/Win32s to prevent resizing while callers inspect bitmap memory.

Dependencies:
- Uses `gdevmswn.h`, `gxdevmem.h`, `gsdll.h`, `gsdllwin.h`, Windows global memory/GDI APIs, Ghostscript memory devices, and common Windows Ghostscript callback/palette helpers.

Research notes:
- The file supports both Win32 and segmented 16-bit Windows memory constraints, which explains much of the block-splitting and alignment logic.
- The DLL row-access API intentionally avoids making a second full bitmap copy when callers only need structured access to rows.
