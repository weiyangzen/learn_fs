# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsovrc.c

Implements the overprint/overprint-mode compositor. It defines serialization for potentially 64-bit `gx_color_index` values using base-128 variable-length bytes, compositor equality, string write/read for command-list use, the public `gs_composite_overprint_type`, `gs_create_overprint`, and `gs_is_overprint_compositor`.

The file defines `overprint_device_t`, a forwarding device with overprint state: `drawn_comps` for non-separable targets and `retain_mask` for separable/linear targets. Three procedure tables represent no-overprint forwarding, generic overprint, and separable overprint. Procedure tables are lazily completed with `gx_device_forward_fill_in_procs`.

Overprint parameter updates choose the correct procedure table, compute process/spot drawn components via color-mapping procedures when retaining spot components, disable overprint for degenerate “all components drawn” cases, and build a byte-order-aware retain mask for separable/linear devices. Little-endian depth > 8 color indexes are byte-swapped for bitmap order.

Device methods open the target and copy parameters, forward `put_params` while syncing open state, forward page-device lookup, and intercept overprint compositor creation by updating the existing overprint device. Rectangle fill methods dispatch to generic or separable overprint helpers, selecting the optimized separable path when depth divides the fill chunk width.

`c_overprint_create_default_compositor` suppresses overprint when no components are retained or when the target has only one component, allocates an overprint forwarding device, copies target parameters, sets the target, and applies overprint parameters. Several comments describe remaining stub/performance areas for additional overprint-specific drawing methods.
