# File Research: sources/virtualization/spdk/lib/nvmf/mdns_server.c

Read completely: yes, 290 lines.

Purpose: optional Avahi-backed mDNS Pull Registration Request publisher for NVMe-oF discovery listeners.

Build condition:
- Entire implementation is guarded by `SPDK_CONFIG_AVAHI`.

Key responsibilities:
- Owns one global Avahi simple poll, client, entry group, and publish context.
- Publishes active discovery subsystem listeners as `_nvme-disc._tcp.local` services.
- Supports updating service entries when listeners change.
- Provides target-scoped stop/destroy helpers.

Control flow:
- `nvmf_publish_mdns_prr()` ensures only one target is published globally, finds the discovery subsystem, requires at least one listener, creates Avahi poll/client objects, stores context, and registers an SPDK poller.
- `publish_client_new_callback()` waits for Avahi running state, then creates an entry group and publishes listeners.
- `nvmf_avahi_publish_iterate()` advances the Avahi simple poll from an SPDK poller.
- `nvmf_tgt_update_mdns_prr()` resets the entry group and republishes listeners.
- `nvmf_tgt_stop_mdns_prr()` unregisters the poller and frees Avahi state if the target matches.

Published service data:
- Service name base is `spdk` plus a per-listener id.
- TCP listeners publish protocol TXT `p=tcp` and discovery NQN TXT.
- RDMA listeners are skipped because the code cannot distinguish RoCE and iWARP.
- Other transport types are rejected for mDNS PRR.

Ownership:
- `nvmf_avahi_publish_destroy()` frees entry group, Avahi client, simple poll, context, and clears globals.
- TXT lists are freed per listener after service add attempt.

Notable edge cases:
- `spdk_nvmf_tgt_find_subsystem()` result is not null-checked before `TAILQ_EMPTY(&subsystem->listeners)`.
- `spdk_strtol()` return is assigned to `uint16_t port` without explicit parse error/range handling.
- Only one target can publish mDNS at a time due to global Avahi state.
