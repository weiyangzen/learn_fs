# File Research: sources/virtualization/nvme-cli/plugins/transcend/transcend-nvme.c

Implements two Transcend commands.

`getHealthValue`:
- Opens device.
- Fetches standard SMART log.
- Prints `100 - percent_used` as health percentage.
- Prints `0%` if `percent_used > 100`.

`getBadblock`:
- Sends admin passthrough opcode `0xc2`.
- Uses CDW10 `0x400`, CDW12 `0x5a`.
- Reads one byte and prints it as bad block count.

Risks/notes:
- Error handling prints `"Device not found"` for any parse/open failure.
- `percent_used` originates from an unsigned byte; the `< 0` check is dead.
