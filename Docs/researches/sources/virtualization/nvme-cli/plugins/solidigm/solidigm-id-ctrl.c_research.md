# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-id-ctrl.c

Solidigm vendor-specific Identify Controller formatter.

Main function:
- `sldgm_id_ctrl(uint8_t *vs, struct json_object *root)`

It interprets the vendor-specific identify-controller bytes as `nvme_vu_id_ctrl_field` and prints either text or appends JSON fields.

Parsed fields include:
- Stripe size, health string, link speed, negotiated link width.
- Security capability/status.
- Bootloader string.
- WWID.
- Bandwidth/IO limit granularity strings.
- Signature, version, product type, NAND type, form factor, firmware status.
- P4 revision, customer ID, usage model.
- Command-set bits: ZNS NVMe, MFND NVMe, CDW14-to-CDW13 mapping, VPD availability.

Notable behavior:
- If `health[0]` is empty, it reports `healthy`.
- JSON uses fixed-length string creation for several fields, preserving embedded/trailing bytes up to field width.
- Numeric fields are mostly printed directly; only `ww` is explicitly little-endian converted.
