# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/bit.c

This file implements libmad's low-level bitstream reader and CRC helper. It owns `mad_bit_init`, `mad_bit_length`, `mad_bit_nextbyte`, `mad_bit_skip`, `mad_bit_read`, and `mad_bit_crc`. The central abstraction is `struct mad_bitptr`, which tracks a byte pointer, cached byte value, and remaining bits in the current byte.

The implementation reads UIMSBF bit fields of arbitrary length, advances byte/bit state, supports skipping ahead, and computes MPEG CRC-16 using the ISO/IEC 11172-3 generator polynomial `0x8005`. The CRC table is static lookup data used by frame and layer decoders to validate protected MPEG frames. `mad_bit_write` is present only in a disabled `#if 0` block, while `bit.h` still declares it.

In the decoder pipeline, this file is foundational: `frame.c`, `layer12.c`, `layer3.c`, and `stream.c` all depend on bit-exact reading. The code assumes callers have already ensured enough guard bytes in the stream buffer; most overrun protection happens at the stream/frame/layer level rather than inside `mad_bit_read`.
