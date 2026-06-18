# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdht.h

This header defines Ghostscript device halftone data structures: halftone cell geometry, whitening orders, order procedure vectors, order storage, order components, and full device halftones.

The opening comment explains the halftone tile model in detail: rational basic cells, multi-cells, rectangular super-cells, physical pixel aspect ratio, frequency/angle conversion, and shifted strip decomposition to avoid materializing very large full super-cells.

`gx_ht_cell_params_t` stores defining rational cell parameters (`M`, `N`, `R`, `M1`, `N1`, `R1`) and derived values (`C`, `D`, `D1`, `W`, `W1`, `S`). `gx_compute_cell_values` fills the derived fields.

Whitening order representation consists of a `levels` array plus `bit_data`. The default bit-data form uses `gx_ht_bit` offset/mask entries, while a short representation is also supported through `ht_order_procs_table`. `ht_sample_t` and `max_ht_sample` are used during sampling.

`gx_ht_order_procs_t` abstracts order implementations with element size, threshold-array construction, bit-index lookup, tile rendering, and a tentative draw method. `gx_ht_order` stores cell params, optional WTS data, dimensions, strip shift/original fields, full height, level/bit counts, procs, allocation memory, levels, bit_data, cache, transfer map, and spot-screen sampling parameters.

`ht_order_is_complete` and `ht_order_full_height` distinguish complete orders from shifted strip orders. GC descriptor macros expose `st_ht_order` and component descriptors.

`gx_device_halftone` contains a primary `gx_ht_order`, reference count, id, halftone type, optional component array, component counts, and LCM tile dimensions. Multi-component halftones parallel process color components and are required for color screens and Type 5 halftones.

The header declares `gx_ht_complete_threshold_order` and `gx_device_halftone_release`.

Filesystem relevance: none. It is graphics halftone model/state.
