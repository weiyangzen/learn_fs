# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdevn.c

Implements common DeviceN/spot-color utilities and two example printer devices: `spotcmyk` and `devicen`.

The shared utilities convert Gray/RGB/CMYK input into DeviceN component arrays using a separation-order map, compute device depth from component count and bits per component, match process/separation colorant names, auto-add spot separations, read/write `SeparationColorNames`, `SeparationOrder`, `MaxSeparations`, and wrap printer parameter updates with rollback on failure.

Device definitions use `spotcmyk_device`, with GC pointer relocation for allocated separation-name strings. `gs_spotcmyk_device` is a 1-bit-per-component CMYK-plus-spot sample; `gs_devicen_device` is an 8-bit DeviceN sample. Both use separation-aware color mapping procs, custom `encode_color`/`decode_color`, and `spotcmyk_get_color_comp_index`.

`spotcmyk_print_page` demonstrates output decomposition: it extracts process-color-model data and individual spot planes from packed scan lines using `repack_data`, writes raw sidecar files, then converts those files to PCX through local PCX header, palette, page, and RLE helpers.

Important dependencies are printer devices (`gdevprn.h`), CRD params, DeviceN declarations in `gdevdevn.h`, equivalent CMYK tracking (`gsequivc.h`), and standard Ghostscript parameter APIs.

Risks: many allocations for separation names are appended without local cleanup on parameter replacement paths. Output filenames are built with `sprintf` from `pdevn->fname`. PCX support is intentionally incomplete for many plane/depth combinations. The sample print path creates multiple files and assumes normal filesystem output, not stdout-like targets.
