# File Research: sources/virtualization/nvme-cli/libnvme/examples/meson.build

This Meson file defines libnvme example executables.

Always built examples:
- `telemetry-listen`
- `display-columnar`
- `display-tree`

Conditional examples:
- If `want_fabrics`: `discover-loop`
- If `want_mi`: `mi-mctp`, `mi-mctp-csi-test`, `mi-mctp-ae`
- If `want_mi` and D-Bus dependency is found: `mi-conf`

Dependencies:
- Common examples use `config_dep`, `ccan_dep`, and `libnvme_dep`.
- `mi-mctp-csi-test` also uses `threads_dep`.
- `mi-conf` also uses `libdbus_dep`.

Integration role:
- Keeps example build selection aligned with optional library features.
