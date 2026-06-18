# File Research: sources/os/bsd/freebsd-src/sbin/hastctl/hastctl.c

`hastctl.c` implements the command-line frontend for HAST administration.

Key behavior:
- Supports commands `create`, `role`, `list`, `status`, and `dump`.
- Reads configuration from `/etc/hast.conf` by default, overrideable with `-c`.
- `create` initializes local metadata and active bitmap directly:
  - Probes local provider.
  - Validates media size, sector size, and extent size.
  - Computes activemap on-disk size.
  - Sets data size, extent size, keepdirty, and local data offset.
  - Writes metadata and zeroes the initial bitmap area.
- `dump` reads and prints on-disk metadata for configured resources.
- `role` sends `HASTCTL_CMD_SETROLE` with `init`, `primary`, or `secondary`.
- `list` and `status` send `HASTCTL_CMD_STATUS`.
- Uses nv pairs over the configured control proto connection to communicate with `hastd`.
- Drops privileges after connecting to the control socket and before sending commands.
- Formats detailed status including role, provider, local path, remote/source addresses, replication mode, dirty bytes, worker pid, statistics, errors, and queue sizes.
- `status` prints a compact tabular view.

Important details:
- `create` defaults extent size to `HAST_EXTENTSIZE` and keepdirty to `HAST_KEEPDIRTY`.
- `all` is accepted for role/list/status/dump where appropriate.
- Unknown resources are reported without aborting the whole multi-resource command unless they determine the final exit code.
