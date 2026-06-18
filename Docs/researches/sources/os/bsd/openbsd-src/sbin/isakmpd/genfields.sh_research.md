# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/genfields.sh

Shell/awk generator that converts a `.fld` packet-field specification into generated field headers and C descriptors.

Generated header:
- Include guard and `field.h`.
- Emits `extern struct field <prefix>_fld[]`.
- Emits structure size macros `<PREFIX>_SZ`.
- Emits offset/length macros.
- Emits typed `GET_*` and `SET_*` macros backed by `field_get_num`, `field_set_num`, `field_get_raw`, and `field_set_raw`.
- Emits extern map arrays for fields with constant maps.

Generated C:
- Includes `constants.h`, `field.h`, generated header, `isakmp_num.h`, and `ipsec_num.h`.
- Emits `struct field` arrays with offset, length, field type, and maps.
- Emits constant-map pointer arrays and field-array terminators.

Important detail:
- The generator supports structure inheritance/continuation by initializing a new section’s offset from the size of a previous prefix when a third token is provided.
