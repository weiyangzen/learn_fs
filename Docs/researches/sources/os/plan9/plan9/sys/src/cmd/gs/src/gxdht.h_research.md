# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdht.h

Defines internal device halftone structures and invariants.

- Documents Ghostscript’s halftone geometry:
  - rational basic cells
  - multi-cells
  - rectangular super-cells
  - strip-based representation for large shifted cells
- Defines `gx_ht_cell_params_t` and `gx_compute_cell_values`.
- Defines halftone bit/order representation:
  - `ht_mask_t`
  - `gx_ht_bit`
  - `ht_sample_t`
  - `max_ht_sample`
- Defines `gx_ht_order_procs_t` with methods:
  - `construct_order`
  - `bit_index`
  - `render`
  - `draw`
- Declares `ht_order_procs_table` with default `gx_ht_bit[]` and compact `ushort[]` representations.
- Defines `gx_ht_order`, including:
  - cell params
  - WTS fields
  - width/height/raster/shift/full height
  - level table
  - bit-data table
  - cache pointer
  - transfer map
  - screen sampling parameters
- Documents strip-order invariants:
  - complete orders have `shift == 0` and `full_height == height`
  - strip orders compute full height from width/shift GCD
- Defines `gx_ht_order_component`, pairing an order with component number/name.
- Defines `gx_device_halftone_s`:
  - default order first for subclassing
  - refcount and id
  - halftone type
  - component array
  - component counts
  - LCM tile dimensions
- Provides GC descriptors for orders, components, and device halftones.
- Declares:
  - `gx_ht_complete_threshold_order`
  - `gx_device_halftone_release`

Important memory rule: halftone substructures are assumed allocated with the same allocator as the device halftone.
