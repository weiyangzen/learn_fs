# File Research: sources/virtualization/nvme-cli/libnvme/examples/telemetry-listen.c

This C example listens for NVMe controller uevents and saves telemetry logs on telemetry asynchronous events.

Core behavior:
- Scans topology and counts controllers.
- Opens each controller’s sysfs `uevent` file.
- Uses `select()` to wait for readable uevent file descriptors.
- Parses lines containing `NVME_AEN=...`.
- Extracts AEN type, info, and log identifier.
- If the event is a telemetry notice, reads controller telemetry via `libnvme_get_ctrl_telemetry`.
- Saves telemetry data to `/var/log/<subsysnqn>-telemetry-<epoch>`.

Important detail:
- The `select()` call uses `nr` as the first argument, but `select()` expects max fd + 1; this example may not be robust if fd values exceed controller count.
- Opens files read-only and writes output with owner/group read permissions.

Integration role:
- Demonstrates sysfs uevent monitoring plus telemetry log retrieval.
