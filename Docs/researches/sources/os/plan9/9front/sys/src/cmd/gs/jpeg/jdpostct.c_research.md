# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdpostct.c

Postprocessing controller for upsampling/color conversion and optional color quantization.

Key points:
- Directly delegates to the upsampler when no color quantization is requested.
- For one-pass color quantization or color precision reduction, uses a strip buffer between upsampling/color conversion and quantizer output.
- For two-pass quantization, can request a full-image virtual sample array, first saving upsampled color-converted rows for quantizer analysis, then replaying them through the quantizer.
- `start_pass_dpost` selects pass-through, save-and-pass, or crank-destination behavior based on buffer mode.
- `post_process_1pass` fills only as much strip data as can be emitted immediately, then quantizes it into the application output buffer.
- `post_process_prepass` scans new rows into the quantizer without emitting pixels and advances output counters for pass progress.
- `post_process_2pass` reads stored strips, clamps to bottom-of-image row count, and emits quantized pixels.

Dependencies and interactions:
- Receives row groups from `jdmainct.c` and invokes `jdsample.c`/`jdmerge.c` plus color quantizers.
- Full-image buffer allocation depends on `QUANT_2PASS_SUPPORTED`.

Risk notes:
- Two-pass paths fail if full-buffer support was not requested or not compiled.
- The one-pass path relies on the upsampler to detect bottom-of-image.
- Buffered-image output before two-pass quantization can reuse the virtual-array strip as temporary workspace.
