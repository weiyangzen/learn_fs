# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/mach64xx.c

Implements broader ATI Mach64/Rage-family support using either legacy I/O register offsets or PCI I/O register mappings. It models CRTC, DAC, LCD, TV, PLL, DSP, memory, drawing, cursor, and configuration registers, with register-name tables for dumps.

`snarf` chooses port vs PCI register access, captures all core registers and PLLs, detects LT/LCD variants, reads LCD registers and panel ID, determines memory-size encoding, and sets framebuffer size plus preferred aperture alignment/size.

`init` handles depths from 1 through 32 bpp with PCI required for >8 bpp, detects enhanced Rage chips, computes/keeps PLLs, configures timing registers, pixel widths, linear aperture eligibility, LCD stretch state, and DSP FIFO parameters from BIOS memory-clock data when enhanced. `load` unlocks CRTC/LCD, programs aperture, timings, LCD registers, DAC/DSP/PLL state, initializes true-color palette grayscale when needed, and marks loaded.

`dump` prints register/PLL/LCD state, decodes VCLKs and pixel clock, and emits ATI BIOS clock/panel table information once. `mach64xxhwgc` is an empty placeholder.
