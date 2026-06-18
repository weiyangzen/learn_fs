# File Research: sources/virtualization/nvme-cli/fabrics.h

This header declares the nvme-cli fabrics command entry points.

Declared functions:
- `fabrics_discovery`
- `fabrics_connect`
- `fabrics_disconnect`
- `fabrics_disconnect_all`
- `fabrics_config`
- `fabrics_dim`

Integration role:
- Exposes fabrics command implementations from `fabrics.c` to nvme-cli command registration and dispatch.
