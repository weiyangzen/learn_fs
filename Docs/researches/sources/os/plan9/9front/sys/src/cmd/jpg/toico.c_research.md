# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/toico.c

ICO writer command that reads one or more Plan 9 images and emits a Windows `.ico` file. It builds the ICO file header, per-icon descriptors, BMP-like icon headers, color maps, XOR pixel masks, and AND transparency masks.

Images are converted to 8-bit grayscale or colormap images when needed. `mkxorand` counts used colors, creates a Plan 9-to-ICO palette map, chooses 1/2/4/8 bpp based on color count, aligns rows to 32-bit boundaries, and writes bottom-up masks.

Transparency is inferred from palette value `0xff` in the AND mask path.
