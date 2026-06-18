# File Research: sources/virtualization/nvme-cli/libnvme/examples/discover-loop.c

This C example discovers loop transport NVMe-oF targets and prints discovery log records.

Core flow:
- Creates a libnvme global context and libnvmf context.
- Configures discovery subsystem over `loop`.
- Scans topology, obtains a host, creates a controller, and adds it to the host.
- Allocates discovery arguments, sets max retries to 4, and calls `libnvmf_get_discovery_log`.
- Disconnects and frees the temporary controller.
- Prints discovery log header and entries as an ASCII tree.

Integration role:
- Demonstrates fabrics discovery without requiring an existing connection, assuming loop targets are configured.
- Exercises `libnvmf_context_create`, `libnvmf_context_set_connection`, topology scan, controller creation, discovery args, and discovery log retrieval.
