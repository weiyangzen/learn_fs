# File Research: sources/virtualization/nvme-cli/plugins/lm/meson.build

This Meson snippet adds LM plugin source files to `plugin_sources`.

Always included:
- `plugins/lm/lm-nvme.c`
- `plugins/lm/lm-print.c`
- `plugins/lm/lm-print-stdout.c`
- `plugins/lm/lm-print-binary.c`

Conditionally included:
- `plugins/lm/lm-print-json.c` only when `json_c_dep.found()`.

Role:
- Keeps LM’s multi-file implementation integrated into the nvme-cli plugin build when the top-level plugin selection includes `lm`.
