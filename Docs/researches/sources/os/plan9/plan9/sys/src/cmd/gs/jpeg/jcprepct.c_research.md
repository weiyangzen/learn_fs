# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcprepct.c

Compression preprocessing controller for color conversion, buffering, downsampling, and edge padding.

Key behavior:
- Buffers color-converted rows until enough rows exist for one downsampling row group.
- Pads the bottom of the image by replicating the final converted row.
- Pads the final output iMCU row vertically to the caller's expected full iMCU height.
- Supports optional context-row mode when input smoothing is compiled in and requested by the downsampler.
- Context mode allocates wrapped row-pointer arrays around three physical row groups so the downsampler can address rows above and below the current group.
- `jinit_c_prep_controller` selects simple or context preprocessing and allocates per-component conversion buffers sized for horizontal edge expansion.

Dependencies:
- Calls color converter and downsampler method pointers.
- Uses component geometry from master setup and row-copy helpers from IJG utilities.

Notable risks:
- Full-buffer preprocessing is not supported and errors if requested.
- Context-row support depends on `INPUT_SMOOTHING_SUPPORTED`; otherwise a downsampler request for context rows fails.
- The code intentionally allows row pointers before the nominal buffer start in context mode.
