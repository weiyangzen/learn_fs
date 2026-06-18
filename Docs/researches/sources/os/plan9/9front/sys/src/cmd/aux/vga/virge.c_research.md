# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/virge.c

Implements S3 Trio64+/ViRGE/Savage-family controller support.

Key responsibilities:
- Unlocks and snarfs extended S3 sequencer/CRT registers.
- Identifies specific chips by CRT ID registers `0x2D/0x2E`.
- Configures PLL limits, aperture size, and memory size by chip family.
- Handles Trio64+, Aurora64V+, Trio64V2, ViRGE, ViRGE/DX/GX/VX/GX2, Savage MX/MV, Savage4/IX, SuperSavage/IXC16, ProSavage variants.
- Rounds virtual width to a multiple of 16 for Savage-family stride requirements.
- Computes width, display mode bits, FIFO thresholds, MMIO mode, and color-mode fields for each chip family.
- Uses `trio64clock` for PLL search and maps results into chip-specific sequencer fields.
- Installs pairwise CRT/sequencer settings and advanced-function register state during `load`.
- Dumps extended CRT/sequencer registers plus DCLK/MCLK derived values.

Important interfaces:
- Exports `Ctlr virge`.
- Depends on `s3generic` and `trio64clock`.
- Uses optional `noclockset` mode attribute.

Notes:
- Contains many hardware-specific comments marking guessed or empirical settings.
- Includes a `newptk`-style safety equivalent for clocks? No; key safety is not here. The notable safeguards are pixel clock validation and optional `noclockset`.
- Supports higher depths for selected ViRGE/Savage variants, unlike `trio64.c`.
