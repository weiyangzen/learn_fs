# File Research: sources/virtualization/spdk/module/bdev/nvme/bdev_mdns_client.c

This file implements optional Avahi/mDNS based NVMe discovery. When built with `SPDK_CONFIG_AVAHI`, it creates Avahi clients and service browsers, resolves matching services, converts resolved TXT/address data into NVMe transport IDs, and starts normal bdev NVMe discovery for each new referral. When Avahi support is absent, all public functions return `-ENOTSUP` or an RPC error.

Runtime state is a global Avahi simple poll object, an Avahi client, and a tailq of `mdns_discovery_ctx` objects. Each context is keyed by a base name and service name, owns an Avahi service browser, driver and bdev controller options, a poller, a sequence counter, and a list of discovered referral entries. Each entry stores the generated discovery name, copied transport ID, copied controller options, and parent context.

Resolution only accepts IPv4 TCP referrals. The resolver extracts `NQN` and `p` TXT keys, maps protocol string `tcp` to `SPDK_NVME_TRANSPORT_TCP`, fills `traddr`, `trsvcid`, `subnqn`, and address family, rejects duplicates with `spdk_nvme_transport_id_compare()`, and schedules `bdev_nvme_start_discovery()` on the SPDK app thread. Service remove events are logged but deliberately do not stop connections; users must stop discovery manually.

`bdev_nvme_start_mdns_discovery()` enforces unique base name and service name, initializes Avahi objects as needed, creates the browser, stores context strings/options, and registers a 100 ms SPDK poller that calls `avahi_simple_poll_iterate()`. Stop marks the context for cleanup, stops all entry discovery sessions by generated name, and lets the poller unregister and free context state. Info/config functions emit active mDNS discovery state and referrals as JSON.

Important invariants are app-thread startup, correct Avahi ownership/freeing, no automatic cleanup on mDNS removal, IPv4-only behavior, and uniqueness of base/service contexts and discovered transport IDs.
