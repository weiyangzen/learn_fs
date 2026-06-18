# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxut.h

This header declares PCL XL generation utilities and operand macros.

Declared high-level API:
- `px_write_file_header`
- `px_write_page_header`
- `px_write_select_media`
- `px_write_file_trailer`

Declared low-level API:
- `px_put_bytes`
- `px_put_a`, `px_put_ac`
- `px_put_ub`, `px_put_uba`
- `px_put_s`, `px_put_us`, `px_put_usa`, `px_put_u`
- `px_put_usp`, `px_put_usq_fixed`
- `px_put_ss`, `px_put_ssp`
- `px_put_l`
- `px_put_r`, `px_put_rl`
- `px_put_data_length`

Macros such as `PX_PUT_LIT`, `DA`, `DUB`, `DS`, `DUS`, and `DUSP` support compact literal byte arrays containing PCL XL typed operands and attributes.

The header documents the important encoding rule used throughout the PCL XL driver: emitted data is little-endian because HP printers only support little-endian data in this path.
