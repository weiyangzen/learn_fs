# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/gfx_private.h

## Role

`gfx_private.h` defines contract-private glue used by AGP, DRM, framebuffer, PCI, and memory-mapping code. It exists to keep illumos kernel graphics support compatible with imported DRM code.

## Key Interfaces and Data

- Defines opaque-ish pointer aliases `gfxp_fb_softc_ptr_t`, `gfxp_acc_handle_t`, and `gfxp_kva_t`.
- Defines memory cache modes: cached, uncached, and write-combined.
- `enum gfxp_type` distinguishes bitmap framebuffer and VGA text mode.
- Provides DDI segmap/devmap and `ddi_umem_cookie_t` helpers.
- Provides PCI config access helpers: init handle, byte/word/dword reads and writes, and device-present probe.
- Provides kernel mapping helpers, VA-to-PA translation, cache attribute fixes, and physical-address conversion.
- Provides framebuffer attach/detach/open/close/ioctl/devmap wrappers.
- Provides user memory lock/unlock helpers for graphics buffers.
- `gfxp_blt_ops` registers blit/copy/clear/setmode hooks; comments note only `setmode` is supplied by current DRM paths.
- `gfxp_bm_fb_info` reports resolution, bits per pixel, and depth.
- Provides kernel-space allocation/load/unload functions and stub-style optional memory-pool APIs with `gfxp_pmem_cookie`.

## Dependencies and Use

This is a private bridge for graphics modules, not a general DDI interface. It intentionally references DRM source expectations in comments.

## Research Notes

The interface is broad but shallow: most declarations are adaptation hooks between illumos VM/DDI mechanisms and upstream DRM helper code.
