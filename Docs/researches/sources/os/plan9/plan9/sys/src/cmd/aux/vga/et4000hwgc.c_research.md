# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/et4000hwgc.c

Hardware graphics cursor eligibility shim for ET4000-W32.

Core behavior:
- `init()` marks itself initialized.
- Sets global `cflag` to disable hardware cursor unless:
  - main controller name starts with `et4000-w32`,
  - depth is 8 bpp,
  - 2x8-bit pixel-clock mode is not active,
  - `cflag` was not already set.

Ctlr:
- `et4000hwgc`

Notable risks:
- Does not implement cursor load/render itself; only controls eligibility for shared cursor logic elsewhere.
