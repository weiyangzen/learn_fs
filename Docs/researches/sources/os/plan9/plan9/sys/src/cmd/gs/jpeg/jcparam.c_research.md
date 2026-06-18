# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcparam.c

Default parameter and table setup for JPEG compression.

Key behavior:
- Builds scaled luminance/chrominance quantization tables from JPEG spec defaults.
- Converts user quality 0..100 into IJG's nonlinear quantization scaling curve.
- Installs standard 8-bit Huffman tables for luminance and chrominance DC/AC coding.
- `jpeg_set_defaults` allocates component info, initializes precision, quality, Huffman/arithmetic defaults, restart defaults, density/JFIF defaults, smoothing, DCT choice, and color-space-dependent component layout.
- Chooses default JPEG colorspace from input colorspace, commonly RGB to YCbCr.
- Sets component IDs, sampling factors, quant tables, and Huffman table selectors for grayscale, RGB, YCbCr, CMYK, YCCK, and unknown color spaces.
- When progressive support is compiled in, `jpeg_simple_progression` builds recommended scan scripts, with a custom 10-scan YCbCr script.

Dependencies:
- Uses permanent memory pool allocation through `jpeg_alloc_quant_table` and `jpeg_alloc_huff_table`.
- Feeds component/table state consumed by master control, FDCT, entropy, and marker writer modules.

Notable risks:
- Most setters are only valid in `CSTATE_START`.
- Standard Huffman tables are marked valid only for 8-bit data; higher precision forces optimized coding.
- Progressive script allocation is retained in the permanent pool and reused when possible.
