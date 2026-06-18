# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht2.c

LanguageLevel 2 `.sethalftone5` implementation for dictionary-based, multi-component halftones. It supports Type 1 spot, Type 3 threshold, and Type 7 threshold2 component dictionaries inside a Type 5 halftone dictionary.

`zsethalftone5` enumerates the component dictionary, maps colorant names to device component numbers with `gs_cname_to_colorant_number`, ignores unusable components, enforces the component limit, allocates a `gs_halftone`, component array, and `gx_device_halftone`, and fills component parameters. It distinguishes Type 2/4 color-screen semantics by using `ht_type_multiple_colorscreen`; otherwise it uses `ht_type_multiple`.

After `gs_sethalftone_prepare`, it writes `ActualFrequency` and `ActualAngle` back into writable spot-function dictionaries when those keys exist. It then schedules Type 1 spot-function sampling and optional transfer-function remapping on the execution stack. `sethalftone_finish` installs the prepared halftone with `gx_ht_install`, and `sethalftone_cleanup` frees temporary prepared structures.

Helper routines parse spot parameters, threshold common parameters, threshold string/byte storage, threshold2 `Width2`/`Height2`/`BitsPerSample`, and convert Ghostscript separation-name indices back to strings for DeviceN/colorant matching.
