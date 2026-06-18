# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer12.c

This file implements MPEG Layer I and Layer II frame decoding. It includes scalefactor data from `sf_table.dat`, Layer I linear scaling constants, Layer II subband quantization tables, bit-allocation tables, offset tables, and quantization classes from `qc_table.dat`.

For Layer I, `I_sample` reads and requantizes a sample, while `mad_layer_I` parses bit allocations, validates CRC when enabled, reads scalefactors, handles joint stereo bounds, and fills `frame->sbsample` for 12 sample groups. For Layer II, `II_samples` handles grouped and ungrouped quantized samples, and `mad_layer_II` selects the appropriate allocation table based on MPEG version, bitrate/channel mode, and sample rate. It decodes allocations, scalefactor selection info, CRC, scalefactors, sample groups, and zero-fills unused subbands.

The output is subband-domain fixed-point data consumed later by synthesis. Error reporting uses `stream->error` values such as bad CRC, bad bit allocation, bad mode, and bad scalefactor. This file is self-contained for Layers I/II and shares only common bit, stream, frame, and fixed-point helpers.
