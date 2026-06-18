# File Research: sources/virtualization/spdk/lib/nvme/nvme_util.c

Provides utility helpers for command-line transport ID usage text, parsing extended transport ID entries, and building human-readable NVMe controller/namespace names.

`spdk_nvme_transport_id_usage()`:
- Prints `-r` / optional `--transport` usage text for transport IDs.
- Adapts output based on flags for mandatory/optional, no PCIe, no fabric, namespace support, host NQN, host address, alternative transport address, and multiple entries.
- Documents accepted keys including `trtype`, fabric `adrfam`, `traddr`, `trsvcid`, `subnqn`, optional `ns`, `hostnqn`, `hostaddr`, and `alt_traddr`.
- Prints PCIe and RDMA examples and a note for multi-target input when enabled.

`spdk_nvme_trid_entry_parse()`:
- Initializes the transport ID to PCIe and default discovery NQN before parsing the generic transport ID string.
- Parses optional `ns:` or `ns=` into a 16-bit namespace ID, rejecting IDs longer than five digits, zero, or greater than 65535.
- Parses optional `hostnqn:`/`hostnqn=`, enforcing destination buffer length.
- Parses optional `hostaddr:`/`hostaddr=`, allowing it only for fabrics transports and enforcing `SPDK_NVMF_TRADDR_MAX_LEN`.
- Initializes `failover_trid` from the primary TRID, then applies optional `alt_traddr:`/`alt_traddr=` with length validation.
- Returns `-EINVAL` on malformed input and logs specific validation errors.

`spdk_nvme_build_name()`:
- Builds readable names by transport type:
  - PCIe: `PCIE (<traddr>)`, optionally adding PCI vendor/device ID when a PCI device is available.
  - RDMA: `RDMA (addr:<traddr> subnqn:<subnqn>)`.
  - TCP: `TCP (addr:<traddr> subnqn:<subnqn>)`.
  - VFIOUSER and CUSTOM with transport address.
- Optionally appends `NSID <id>` when a namespace is provided.
- Returns formatting errors when `snprintf()` fails or unknown transport type is encountered.

Implementation notes:
- Uses case-insensitive substring searches for extension keys, supporting both colon and equals separators.
- Parsing is simple and whitespace-delimited; it assumes values do not contain spaces.
- The `hostnqn += strlen("hostnqn:")` style also works for `hostnqn=` because the key length is the same.

Filesystem/storage relevance:
- This file supports operational tooling and user input for selecting NVMe block devices and namespaces. It is not on the data path, but it shapes how local PCIe and NVMe-oF targets are identified, named, and configured by SPDK applications.
