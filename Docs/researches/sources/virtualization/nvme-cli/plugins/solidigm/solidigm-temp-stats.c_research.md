# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-temp-stats.c

Implements `temp-stats`, which fetches and displays Solidigm temperature statistics.

Main behavior:
- Fetches LID `0xd5`.
- On positive status, falls back to legacy LID `0xc5`.
- Encodes Solidigm UUID index in CDW14.
- Supports `--raw-binary`.

Data model:
- `struct temp_stats` contains current temperature, overtemp flags, lifetime high/low, max/min operating temps, and estimated offset.

Special handling:
- When legacy `0xc5` succeeds, checks bytes near offset 4080 for an OCP Unsupported Requirements GUID and rejects with `-EBADMSG` if present.

Output:
- Normal mode prints named 64-bit fields.
- Raw mode dumps only `sizeof(struct temp_stats)`.
