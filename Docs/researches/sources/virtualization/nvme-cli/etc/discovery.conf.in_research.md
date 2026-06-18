# File Research: sources/virtualization/nvme-cli/etc/discovery.conf.in

This is the template for the default NVMe-oF discovery configuration file.

Content:
- Comments explain that the file is used to extract default discovery parameters.
- Gives an example discovery line using `--transport`, `--traddr`, `--trsvcid`, `--host-traddr`, and `--host-iface`.

Integration role:
- Consumed by `fabrics.c` via the installed path represented by `PATH_NVMF_DISC`.
- Provides line-oriented CLI-style defaults for discovery when no explicit CLI parameters are supplied.
