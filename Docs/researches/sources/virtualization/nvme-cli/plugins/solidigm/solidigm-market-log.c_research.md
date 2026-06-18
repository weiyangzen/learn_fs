# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-market-log.c

Implements `market-log`, which fetches Solidigm vendor log page `0xdd`.

Main behavior:
- Parses `--raw-binary`.
- Opens the NVMe device and resolves the Solidigm UUID index.
- Issues Get Log for LID `0xdd`, namespace all, CSI NVM, 512-byte buffer.
- Encodes UUID index in CDW14.
- Prints `"Solidigm Marketing Name Log"` as text unless raw mode is requested.

Risks/notes:
- Treats the fetched log as a C string in text mode; malformed or unterminated data could print beyond meaningful content within the buffer formatting path.
