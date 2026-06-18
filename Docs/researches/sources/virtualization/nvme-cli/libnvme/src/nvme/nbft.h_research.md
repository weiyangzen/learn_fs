# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nbft.h

## Role

Public libnvme NBFT API and data model header. It defines libnvme's parsed NBFT representation, public read/free functions, and a linked-list wrapper used for collections of parsed NBFT files.

## Public Data Structures

- `enum libnbft_primary_admin_host_flag`: administrative host priority hint values.
- `struct libnbft_host`: host UUID pointer, host NQN, configured flags, and primary administrative flag.
- `struct libnbft_hfi_info_tcp`: decoded TCP HFI transport info, including PCI routing ID, MAC, VLAN, IP addresses, DNS/DHCP data, route metric, hostname, and route/DHCP flags.
- `struct libnbft_hfi`: HFI descriptor index, transport string, and TCP transport info.
- `struct libnbft_discovery`: discovery descriptor index, optional security/HFI links, discovery URI, and discovery controller NQN.
- `struct libnbft_security`: security descriptor index placeholder with TODO for additional fields.
- `enum libnbft_nid_type`: namespace identifier types: none, EUI-64, NGUID, namespace UUID.
- `struct libnbft_subsystem_ns`: parsed subsystem namespace descriptor, including descriptor links, HFI array, transport endpoint, namespace identifiers, NQN, digest flags, extended-info fields, and availability/discovery flags.
- `struct libnbft_info`: top-level parsed table object containing filename, raw table bytes/size, host, and null-terminated descriptor lists.
- `struct nbft_file_entry`: linked-list node for storing parsed NBFT objects.

## Public Functions

- `libnvmf_read_nbft(ctx, nbft, filename)`: reads and parses a raw ACPI NBFT table file.
- `libnvmf_free_nbft(ctx, nbft)`: releases the parsed NBFT object and all owned allocations.

## Dependencies

Includes:

- `stdbool.h`
- `sys/types.h`
- `nvme/nvme-types-nbft.h`

The public structs use NBFT/NVMe integer typedefs and expose borrowed pointers into the raw NBFT backing buffer for strings and IDs.

## Notes

The header documents the intended parsed model more fully than `nbft.c` currently implements. In particular, `struct libnbft_security` is a placeholder, and `libnbft_host.primary` is defined but not populated by the current parser.
