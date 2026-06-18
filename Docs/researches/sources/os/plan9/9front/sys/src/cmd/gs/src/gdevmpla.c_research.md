# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmpla.c

## Role

Planar memory device implementation. It lets a Ghostscript memory device store color data in separate planes while presenting a normal device interface.

## Main API

- `gdev_mem_set_planar(gx_device_memory *mdev, int num_planes, const gx_render_plane_t *planes)` is the public setup function.

## Main Behavior

- Validates plane count, plane depth, shifts, overlap, supported memory depth, and total depth.
- Copies plane descriptors into the memory device and replaces drawing/get-bits procedures with planar-aware versions.
- `mem_planar_open` opens only devices with `num_planes != 0`.
- Drawing operations temporarily patch the memory device to one plane at a time:
  - `mem_planar_fill_rectangle`
  - `mem_planar_copy_mono`
  - `mem_planar_copy_color`
  - `mem_planar_strip_tile_rectangle`
- `planar_to_chunky` repacks planar storage back into chunky pixel data, including fast direct cases for 8-bit component RGB/RGBA-like layouts.
- `mem_planar_get_bits_rectangle` either returns one selected plane through the normal memory get-bits path or repacks to chunky output.

## Data Handling

The code uses `line_ptrs` as consecutive per-plane line-pointer tables. During per-plane operations it advances `mdev->line_ptrs` by `mdev->height` per plane, then restores saved device state.

## Risks and Edge Cases

- The implementation mutates the device structure while delegating to prototype device procedures; it relies on strict restoration paths.
- `copy_color` and generic get-bits use fixed stack buffers and chunk transfers to avoid large temporary allocation.
- Colored tiles cannot be split into planes and are delegated to the default strip-tile implementation.
