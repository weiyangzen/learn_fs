# File Research: sources/os/plan9/9front/sys/src/cmd/scat/sky.h

Purpose: Primary shared header for `scat`, defining catalog formats, record types, image/plate structures, globals, and prototypes.

Key content:
- Type enum for planets, patches, SAO, NGC/IC, Messier, named records, Abell, NGC object categories, and internal expansion types.
- Packed on-disk record structs: `NGCrec`, `Abellrec`, `Planetrec`, `SAOrec`, `Mindexrec`, `Bayerec`.
- Runtime `Record` union and `Patchrec`.
- Plate and DSS image structs: `Plate`, `Header`, `Img`, `Picture`.
- Unit macros for radians/degrees/arcseconds/milliarcseconds.
- Global declarations for catalog records, plate inventory, display state, gamma, bbox, and output.

Integration: Included by nearly every scat source file. It is the source of truth for binary catalog layout and cross-module function signatures.

Risks:
- Header defines non-extern globals (`nplate`, `plate`, `PI_180`, `gam`, etc.), which works only under Plan 9's build/link expectations or single-definition discipline.
- Packed structures are layout-critical.
- `Key` is explicitly assumed to be 4 bytes.
