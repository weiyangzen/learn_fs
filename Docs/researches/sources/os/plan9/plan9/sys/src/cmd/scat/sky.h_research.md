# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/sky.h

Primary shared header for `scat`.

Key contents:
- Documents catalog key encoding and record categories.
- Defines `Type` values for planets, patches, SAO, NGC, M, named records, Abell, NGC subtypes, and internal placeholders.
- Defines DSS plate parameter indexes.
- Defines core scalar types: `Angle`, `DAngle`, `Mag`, `Key`, and `Pix`.
- Defines on-disk/in-memory records: `NGCrec`, `Abellrec`, `Planetrec`, `SAOrec`, `Mindexrec`, `Bayerec`, `Namerec`, `Patchrec`, `Record`, `Name`, `Plate`, `Header`, `Img`, and `Picture`.
- Declares global catalog, plate, plotting, gamma, bounding-box, and output state.
- Declares cross-file functions for catalog loading, coordinate conversion, DSS decoding, plotting, display, parsing, and formatting.

Behavior notes:
- On-disk integer fields are explicitly noted as little-endian.
- `DIR` defaults catalog data to `/lib/sky`.
