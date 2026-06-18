# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-nbft.h

## Role

Defines ACPI NVMe Boot Firmware Table types for NVMe-oF boot configuration. The structures describe firmware-provided pre-OS boot state for NVMe/TCP interfaces, namespaces, security settings, and discovery controllers.

## Key Content

- Defines NBFT descriptor IDs in `enum nbft_desc_type`, including header, control, host, HFI, SSNS, security, discovery, HFI transport info, SSNS extended info, and HFI extended info.
- Defines NBFT transport type `NBFT_TRTYPE_TCP` and table signature `NBFT_HEADER_SIG`.
- Defines heap object references with `struct nbft_heap_obj`, used throughout the table to point at variable-length heap strings or descriptor objects.
- Models the ACPI-style table header:
  - `struct nbft_header`
- Models control-plane descriptor placement:
  - `struct nbft_control`
  - `enum nbft_control_flags`
- Models host identity:
  - `struct nbft_host`
  - `enum nbft_host_flags`
- Models host fabric interfaces:
  - `struct nbft_hfi`
  - `enum nbft_hfi_flags`
  - `struct nbft_hfi_info_tcp`
  - `enum nbft_hfi_info_tcp_flags`
- Models subsystem namespace boot targets:
  - `struct nbft_ssns`
  - `enum nbft_ssns_flags`
  - `enum nbft_ssns_trflags`
  - `struct nbft_ssns_ext_info`
  - `enum nbft_ssns_ext_info_flags`
- Models security policy:
  - `struct nbft_security`
  - `enum nbft_security_flags`
  - `enum nbft_security_secret_type`
- Models discovery controllers:
  - `struct nbft_discovery`
  - `enum nbft_discovery_flags`

## Dependencies

- Includes `nvme/lib-types.h`.
- Uses `__attribute__((packed))` for structures where firmware table byte layout must not include compiler padding.
- Uses endian-tagged integer aliases for ACPI/NBFT serialized fields.

## Research Notes

This header is pure layout definition. Its important design pattern is indirection through `struct nbft_heap_obj`, where fixed descriptors point into a heap area. Consumers must validate table length, heap bounds, descriptor counts, descriptor lengths, and checksum before trusting offsets. Several flags encode policy state, not merely capabilities, for example administratively configured host identity, DHCP overrides, secure-channel requirements, and namespace availability hints.

## Filesystem/Storage Relevance

NBFT is relevant to boot-from-fabric systems: it tells the OS how firmware connected to NVMe/TCP boot storage and how to rediscover or reestablish that connection. This sits below filesystems, but it directly affects root-device discovery in virtualized or network-boot storage environments.
