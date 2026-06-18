# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/udev-rules/70-nvmf-autoconnect.rules.in

- Purpose: udev rules for NVMe-oF autoconnect on discovery log changes and FC discovery events.
- Trigger scope: only `ACTION=="change"` events.
- Compatibility: sets empty `NVME_HOST_IFACE` to `none` for older expectations.
- Discovery AEN handling: on NVMe discovery log change AEN `0x70f002`, restarts a specific `nvmf-connect@...service` instance with device, transport, traddr, trsvcid, host-traddr, and host-iface arguments.
- FC handling: supports old-style FC `FC_EVENT=="nvmediscovery"` events and restarts the templated service with FC-specific arguments.
- Rediscover handling: when a discovery controller reconnects with `NVME_EVENT=="rediscover"`, rereads the discovery log through the templated service.
