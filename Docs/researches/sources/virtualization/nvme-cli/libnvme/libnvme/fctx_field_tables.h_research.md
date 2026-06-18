# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/fctx_field_tables.h

This generated header maps Python/user-facing fabrics config keys to offsets inside `struct libnvme_fabrics_config`.

Data structures:
- `struct fctx_field { const char *key; size_t off; }`
- Integer fields: queue sizing, reconnect and timeout fields, ToS.
- Long fields: keyring and TLS key IDs.
- Boolean fields: duplicate connect, SQ flow disable, header/data digest, TLS, concat.
- `libnvme_fabrics_config_keys[]`: full key list for validation/introspection.

Integration role:
- Used by Python binding support code to validate and populate fabrics controller dictionaries.
- Generated from `private.h` and updated via Meson `update-accessors`.
