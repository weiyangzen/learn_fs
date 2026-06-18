# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcprepct.c

Compression preprocessing controller for color conversion, downsampling input buffering, and vertical edge padding.

Key points:
- Buffers color-converted rows until enough rows are available for the downsampler’s row-group contract.
- Simple mode buffers one row group and pads the bottom of the image by replicating the last row.
- Context-row mode, enabled only when input smoothing support needs it, uses wrapped row-pointer arrays around three real row groups so downsamplers can inspect rows above and below.
- `start_pass_prep` resets rows remaining and buffer position.
- `pre_process_data` converts input rows, pads bottom rows, invokes the downsampler, and pads final output rows to full iMCU height.
- `pre_process_context` fills and rotates context buffers, creates top/bottom dummy context rows, and downscales row groups when enough input is available.
- `jinit_c_prep_controller` rejects full-buffer requests, allocates the prep controller, chooses simple vs context processing, and allocates per-component color buffers wide enough for horizontal edge expansion.

Dependencies and interactions:
- Calls `cconvert->color_convert` from `jccolor.c` and `downsample->downsample` from `jcsample.c`.
- Feeds the main controller’s component strip buffers.

Risk notes:
- Context mode is available only if `INPUT_SMOOTHING_SUPPORTED` compiled it in.
- Assumes the caller supplies one-iMCU-height output buffers.
- Buffer dimensions are tied to component sampling factors computed by master setup.
