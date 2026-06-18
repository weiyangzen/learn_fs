# File Research: sources/virtualization/nvme-cli/libnvme/scripts/collect-sysfs.sh

This Bash helper archives NVMe-related sysfs directories for debugging.

Core behavior:
- Builds filename `nvme-sysfs-<hostname>-<kernel>.tar.xz`.
- Collects fixed sysfs paths for nvme classes and PCI slots.
- Adds real paths for entries under each directory via `readlink -f`.
- Creates a compressed tar archive, preserving permissions, suppressing stderr.

Integration role:
- Diagnostic data collection script for topology/sysfs issues.
