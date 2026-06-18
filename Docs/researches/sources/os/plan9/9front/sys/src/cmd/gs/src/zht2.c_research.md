# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zht2.c

## Purpose
Implements Level 2 `.sethalftone5` support for multi-component halftone dictionaries, including spot, threshold, and threshold2 components.

## Key Functions
- `gs_get_colorname_string()` converts a separation/colorant name index to string data.
- `zsethalftone5()` parses the primary and component halftone dictionaries, prepares device halftones, schedules sampling, and installs the result.
- `sethalftone_finish()` installs the prepared halftone.
- `dict_spot_params()` parses Type 1 spot halftone parameters.
- `dict_spot_results()` writes actual frequency/angle results back to dictionaries.
- `dict_threshold_params()` and `dict_threshold2_params()` parse threshold halftone data.

## Important Behavior
- Counts only component dictionaries matching usable device colorants; ignores unrelated dictionary entries.
- Type 2 and Type 4 halftones are marked as multiple colorscreens so they adapt to the device color space.
- Supports component HalftoneTypes 1, 3, and 7.
- Schedules both spot-function sampling and transfer-function remapping on the execution stack.
- Threshold2 supports string or byte-structure threshold storage and validates size against dimensions and bits per sample.

## Research Notes
This is the most complex halftone interpreter bridge in the group, coordinating dictionaries, colorant names, VM spaces, graphics state, and deferred execution.
