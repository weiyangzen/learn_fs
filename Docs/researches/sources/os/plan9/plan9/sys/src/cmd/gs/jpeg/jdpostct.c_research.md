# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdpostct.c

Purpose: decompression postprocessing controller for upsampling/color conversion and color quantization buffering.

Key structures and routines:
- `my_post_controller` extends `jpeg_d_post_controller` with an optional full-image virtual array, strip buffer, strip height, and strip row state.
- `start_pass_dpost()` selects one-pass, first-pass quantization, second-pass quantization, or pass-through behavior.
- `post_process_1pass()` runs upsampling into a strip buffer and then quantizes/emits rows.
- `post_process_prepass()` runs first pass of two-pass quantization, saving converted rows to a virtual full-image buffer and feeding the quantizer statistics.
- `post_process_2pass()` reads saved rows from the virtual buffer and emits quantized output.
- `jinit_d_post_controller()` allocates strip or full-image quantization buffers when needed.

Important behavior:
- If no color quantization is required, this controller delegates directly to the upsampler.
- Two-pass quantization requires a virtual full-image buffer rounded to the strip height.
- Strip height is `max_v_samp_factor`, matching efficient upsampler output granularity.
- In prepass, `out_row_ctr` is advanced even though no output is emitted so the caller can track completion.

Dependencies:
- Upsampler, color quantizer, JPEG memory manager virtual arrays, buffer-mode enum.

Notes:
- This controller is mostly bypassed for simple non-quantized output.
