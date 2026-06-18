# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevperm.c

Ghostscript printer test device that permutes color components to exercise DeviceN and color-component assumptions.

Key behavior:
- Defines a `permute` printer device that normally behaves like CMYK contone output and emits a PPM image.
- With `Permute=1`, changes the internal model to DeviceN with six components arranged as yellow, cyan, cyan2, magenta, zero, black, then converts back to RGB for output.
- Supports `Mode=0` for CMYK-like behavior and `Mode=1` for CMY behavior.
- `perm_print_page` reads raw rendered component data, optionally unpermutes components, converts CMYK/CMY to RGB, and writes binary PPM (`P6`).
- Provides color mapping procs for gray/RGB/CMYK input in both modes, with optional permutation through `perm_permute_cm`.
- Implements component-name lookup against the active colorant-name list.
- Implements generic 8-bit-per-component `encode_color` and `decode_color`.
- `perm_get_params` writes `Permute`, `Mode`, and, when permuting, `SeparationColorNames`.
- `perm_set_color_model` switches device color model metadata, component count, depth, polarity, and colorant names.
- `perm_put_params` reads and validates parameters, updates color model, delegates to printer parameter handling, and restores old color info on failure.

Research notes:
- The device is explicitly for regression testing DeviceN/color-cleanliness paths.
- It is useful for finding code that assumes only DeviceGray, DeviceRGB, or DeviceCMYK.
