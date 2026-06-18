# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcinit.c

Compression pipeline initializer.

Key behavior:
- Initializes compression master control, which validates parameters and derives image/scan geometry.
- For normal input, initializes color conversion, downsampling, and preprocessing; raw downsampled input bypasses those modules.
- Initializes FDCT, entropy encoder, coefficient controller, main controller, and marker writer.
- Chooses progressive Huffman encoder when progressive mode is active and compiled in; arithmetic coding is rejected as not implemented.
- Requests realization of virtual arrays after all modules have declared their needs.
- Writes SOI and optional early file header markers immediately, while frame/scan headers are deferred.

Dependencies:
- Coordinates the compression-side IJG module init functions and relies on the memory manager's virtual-array realization hook.

Notable risks:
- Arithmetic coding is explicitly unavailable in this build path.
- Progressive compression requires `C_PROGRESSIVE_SUPPORTED`; otherwise initialization fails.
- Linking this file pulls in the full compression library, which is why transcoding uses a separate path.
