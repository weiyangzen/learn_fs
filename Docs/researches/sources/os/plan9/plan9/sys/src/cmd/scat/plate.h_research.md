# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/plate.h

Provides an older/standalone DSS plate header interface.

Key contents:
- Defines plate parameter indexes matching the DSS header parser: PPO terms, AMD X/Y polynomial terms, plate scale, pixel sizes, and plate RA/Dec fields.
- Defines `Angle`, `Plate`, `Header`, `Type`, and a flexible `Image` record.
- Declares global plate/gamma/debug state and image/coordinate decoding functions.

Behavior notes:
- Much of this overlaps with the later `sky.h` definitions.
- Some prototypes reflect older names/types, such as `Bitmap* image(...)`, while current `scat` uses `Picture* image(...)` through `sky.h`.
