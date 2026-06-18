# File Research: sources/teaching/minix/minix/fs/procfs/service.c

`service.c` implements the dynamic `/proc/service` directory. It snapshots RS process tables into a local `rproc` transfer structure, creates one file per active system service, and generates per-service details.

`service_get_policies` currently uses a built-in label-to-policy mapping rather than querying RS policy state. It formats policy names such as `reset` and `restart` into a per-slot buffer. `service_get_flags` formats RS and system flags into a compact character string for active/updating/exiting/no-ping/copy/replication/core-service status.

`service_active` filters RS slots down to live system services, excluding init's user-process representation. `service_update` fetches RS tables, deletes stale service entries in one pass, then adds missing active services in a second pass to avoid name-collision issues. `service_init` creates the static `service` directory under the VTreeFS root.

`service_lookup` lazily refreshes the directory once per clock tick for lookups inside `/proc/service`. `service_getdents` refreshes before listing. `service_read` emits a service file with filename, endpoint, pid, restart count, formatted flags, policy string, and ASR count.
