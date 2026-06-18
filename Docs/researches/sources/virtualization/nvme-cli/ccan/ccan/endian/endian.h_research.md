# File Research: sources/virtualization/nvme-cli/ccan/ccan/endian/endian.h

- Purpose: endian-aware integer typedefs and conversion helpers.
- Key APIs: constant byte-swap macros, runtime `bswap_*` fallbacks, `CPU_TO_LE*`, `LE*_TO_CPU`, `CPU_TO_BE*`, `BE*_TO_CPU`, and inline `cpu_to_*`/`*_to_cpu` functions.
- Types: defines `leint16_t`, `leint32_t`, `leint64_t`, `beint16_t`, `beint32_t`, and `beint64_t`; integrates with `short_types.h` for `le16/be16` aliases.
- Safety: errors out if target endian is unknown or both big/little are selected.
- Sparse support: uses bitwise/force attributes under `__CHECKER__`.
