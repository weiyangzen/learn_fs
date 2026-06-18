# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readjpg.c

## Purpose
JPEG decoder returning `Rawimage` data in either YCbCr or RGB channel form.

## Format Support
Handles SOI/EOI, APP/COM, DQT, DHT, SOF0 baseline Huffman, SOF2 progressive Huffman, SOS, DRI restart intervals, one- and three-component images, quantization, Huffman entropy decoding, IDCT, chroma subsampling, and color conversion.

## Implementation
`Header` stores bitstream state, frame components, quantization tables, Huffman tables, MCU block buffers, progressive coefficient storage, and output image state. Baseline scans decode MCU blocks directly, dequantize, IDCT, and map into channels. Progressive scans accumulate DC/AC coefficients across scans, then run IDCT at EOI.

## Color Handling
Can preserve YCbCr or convert to RGB using fixed-point coefficients. `colormap1`, `colormapall1`, and `colormap` handle grey, simple 1x1 sampling, and general subsampling.

## Error Handling
Uses `setjmp`/`longjmp` cleanup, marker recovery for entropy peek-ahead, restart validation, and explicit errors for unsupported DNL/arithmetic/hierarchical modes.
