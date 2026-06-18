# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/header.c

Parses telemetry log header and reason identifier data into JSON.

Main components:
- `sldm_uint8_array_to_string()` converts byte arrays into JSON strings, stopping at NUL unless nonzero data follows.
- Packed structs model Solidigm reason identifier versions 1.0, 1.1, 1.2, and OCP 2.5.
- Static asserts ensure modeled reason identifier structs match the NVMe telemetry reason identifier field size.

Top-level output:
- Root key `telemetryHeader`.
- Fields include log identifier, IEEE OUI bytes, data area last blocks, host/controller generation fields, and `reasonIdentifier`.

Reason identifier parsing:
- OCP mode emits OCP fields: `errorId`, `fileId`, `lineNum`, valid flags, reserved, and VU extension.
- Solidigm mode emits version, reason code, drive status, and version-specific fields.
- Version 1.1+ includes `oemDataMapOffset`.
- Version 1.2 includes product family and dual-port reserved data.

Risks/notes:
- Some 8-bit telemetry version fields are passed through `le16_to_cpu()`, which is harmless but semantically odd.
