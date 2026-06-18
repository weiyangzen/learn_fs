# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sjpeg.h

Declares Ghostscript wrapper entry points around IJG libjpeg.

Key points:
- Explains that wrappers take `stream_DCT_state *` instead of raw IJG structs and convert IJG error exits into Ghostscript-style error return values.
- Declares common error setup/logging, quantization/Huffman table allocation, and destroy helpers.
- Declares encode wrappers for compressor creation, defaults, colorspace, quality, start, scanline write, and finish.
- Declares decode wrappers for decompressor creation, header read, start, scanline read, and finish.

Research relevance:
- This is the interface boundary between Ghostscript DCT streams and IJG libjpeg.
