# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevemap.c

Static encoding map tables between PostScript StandardEncoding and ISO Latin-1.

Key contents:
- `gs_map_std_to_iso[256]`
- `gs_map_iso_to_std[256]`

Risks / notes:
- Data-only table file; zero entries indicate unmapped code points.
