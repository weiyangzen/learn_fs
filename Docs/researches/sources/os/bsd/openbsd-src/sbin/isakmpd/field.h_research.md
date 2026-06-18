# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/field.h

Declares the generated-field descriptor type and accessor API.

`struct field` contains:
- Field name.
- Byte offset.
- Length.
- Type enum: `raw`, `num`, `mask`, `ign`, `cst`.
- Optional constant maps.

This header is used by generated protocol field headers and by code that uses `GET_*`/`SET_*` macros produced by `genfields.sh`.
