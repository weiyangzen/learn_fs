# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/cyber938x.c

Implements Trident Cyber938x-family setup. It includes DAC Pixel Command Register access via the classic four-read Pixmask unlock sequence and stores old/new sequencer state plus inferred LCD panel dimensions.

`snarf` switches between old/new register modes, captures sequencer/CRT/graphics ranges, determines VRAM size from CRTC bits, and infers panel size from graphics register `0x52`. `init` enables linear mode if requested, sets scaling selectors by vertical size, configures pixel bus/PCR values for 8/16/24 bpp, and applies revision-specific register tweaks for Cyber/ProVidia/CyberBlade variants.

`load` switches the chip into new mode, writes PCR, graphics, CRT, and linear-aperture bits. `dump` prints extended register ranges, VCLK decoding, and LCD size.
