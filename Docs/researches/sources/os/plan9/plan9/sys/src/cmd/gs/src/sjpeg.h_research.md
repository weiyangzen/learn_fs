# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpeg.h

Header declaring Ghostscript wrapper entry points for IJG libjpeg operations.

Key contents:
- Common wrappers for error setup/logging, quant/huffman table allocation, and JPEG destroy.
- Encode wrappers for compressor creation, defaults, colorspace, quality, start/write/finish.
- Decode wrappers for decompressor creation, header reading, start/read/finish.

Notable dependencies:
- Requires `sdct.h` and IJG `jpeglib.h` context in users.

Research notes:
- The wrappers convert IJG `longjmp` error exits into Ghostscript-style return codes.
- Allocation wrappers return `NULL` for VM-style allocation failure.
