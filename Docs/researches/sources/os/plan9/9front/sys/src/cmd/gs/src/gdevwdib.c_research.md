# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevwdib.c

## Purpose
Microsoft Windows Ghostscript display/DLL driver using a device-independent bitmap (DIB) memory backing store.

## Main Concepts
- Defines `gx_device_win_dib`, extending Windows common device state with DIB memory, optional Win32 mutex, lock count, and an embedded Ghostscript memory device.
- Registers the `mswindll` device.
- Exposes DLL APIs for copying the DIB, copying the palette, drawing the bitmap to a caller HDC, locking the device, and retrieving bitmap rows.

## Key Functions
- `win_dib_open`: opens common Windows state, creates a mutex on non-Win32s, validates memory-device support, allocates bitmap memory, and notifies DLL callbacks.
- `win_dib_get_initial_matrix`: uses a lower-left origin suitable for DIB memory.
- `win_dib_close`: locks, notifies callback shutdown, frees bitmap memory, closes mutex, and closes common Windows state.
- Drawing wrappers: `win_dib_fill_rectangle`, `win_dib_copy_mono`, `win_dib_copy_color`, `win_dib_get_bits`; these delegate to the embedded memory device and split transfers around 64K segment boundaries on 16-bit Windows.
- `win_dib_put_params`: locks around Windows parameter updates.
- DLL exports:
  - `gsdll_copy_dib`
  - `gsdll_copy_palette`
  - `gsdll_draw`
  - `gsdll_lock_device`
  - `gsdll_get_bitmap_row`
- `win_dib_repaint`: pushes DIB rows to a Windows DC with `SetDIBitsToDevice`, chunking large transfers.
- `win_dib_make_dib`: allocates a standalone DIB copy with header, palette/bitfields, and pixel data.
- `win_dib_alloc_bitmap`, `win_dib_free_bitmap`: allocate global memory for raster data and line pointers.
- `win_dib_lock_device`: mutex/lock-count helper for external access.

## Notable Risks
- 16-bit segment splitting code is delicate; one copy-color split branch advances the source by `by * raster` rather than `bh * raster`.
- Several allocation/lock paths beep or return null without detailed error propagation.
- `gsdll_get_bitmap_row` assumes a valid device pointer and accesses fields before full validation.
- External callers can receive row pointers valid only while locked; misuse can race with Ghostscript drawing or resizing.

## Filesystem Relevance
No filesystem implementation logic. The DLL row-copy API can support saving bitmaps externally, but this file only manages in-memory DIB output and Windows drawing.
