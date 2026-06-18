# File Research: sources/virtualization/nvme-cli/plugins/nbft/nbft-plugin.c

## Role

Implements the `nvme nbft show` command for displaying ACPI NBFT tables. NBFT data is read through libnvme fabrics/NBFT helpers, then formatted as normal text tables or JSON.

## Public Entry Point

`show_nbft()` is the only command handler. It supports options:

- `--subsystem` / `-s`: show NBFT subsystems.
- `--hfi` / `-H`: show Host Fabric Interfaces.
- `--discovery` / `-d`: show discovery controllers.
- `--nbft-path`: override the default ACPI table path.

Default NBFT table path is `/sys/firmware/acpi/tables`.

If none of subsystem/HFI/discovery are requested, all three are shown.

## Data Sources

`show_nbft()` creates a libnvme global context and calls:

- `libnvmf_nbft_read_files(ctx, nbft_path, &head)`
- `libnvmf_nbft_free(ctx, head)`

The parsed records are linked as `struct nbft_file_entry` values, each carrying a `struct libnbft_info`.

## Formatting Helpers

Normal output:

- `normal_show_nbfts()`
- `normal_show_nbft()`
- `print_nbft_subsys_info()`
- `print_nbft_hfi_info()`
- `print_nbft_discovery_info()`
- `print_hfis()`

JSON output when `CONFIG_JSONC` is enabled:

- `json_show_nbfts()`
- `nbft_to_json()`
- `hfi_to_json()`
- `ssns_to_json()`
- `discovery_to_json()`

If JSON-C is not compiled in, `json_show_nbfts` is a macro returning `-EINVAL`.

## Structure Conversion

The file translates libnbft structures into user-facing fields:

- Host: NQN, host ID, configured flags, primary admin host flag.
- HFI TCP info: PCI SBDF, MAC, VLAN, IP origin/address, subnet, gateway, route metric, DNS, DHCP server, hostname, default route, DHCP override.
- Subsystem namespace: transport, traddr, trsvcid, subsys port ID, NSID, NID type/value, NQN, controller ID, ASQ size, root path, digest requirements, discovered/unavailable flags.
- Discovery controller: security index, HFI index, URI, NQN.

## Small Utilities

- `pci_sbdf_to_string()` formats segment/bus/device/function from encoded SBDF.
- `mac_addr_to_string()` formats six-byte MAC addresses.
- `primary_admin_host_flag_to_str()` maps libnbft host primary flag enum values.
- Static `dash[100]` is used for table separators.

## Output Behavior

Normal output dynamically sizes some table columns based on field lengths, especially IP/gateway/DNS/NQN/URI/address/HFI list widths. Subsystem HFI lists are truncated with dots if they exceed `HFIS_LEN`.

JSON output builds arrays of NBFT records, with nested host/subsystem/HFI/discovery objects or arrays depending on requested sections.

## Dependencies

Includes and relies on:

- `libnvme.h`
- `nvme-print.h`
- `nvme.h`
- `fabrics.h`
- `logging.h`
- JSON helper APIs under `CONFIG_JSONC`
- nvme-cli `argconfig`, output format, and logging globals.

## Notes

- The file is a read-only display tool; it does not issue NVMe admin commands to devices.
- It is Linux/ACPI-path oriented through the default sysfs firmware table path.
- JSON construction has fail paths that free the top-level object; some intermediate JSON arrays/objects depend on json-c ownership transfer behavior.
