# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nsid.c

Purpose: Implements `nvmecontrol nsid`, a helper command that maps a namespace character device to its controller and namespace ID.

Key behavior:
- Registers top-level command `nsid`.
- Opens the provided namespace/controller device read-only.
- Calls `get_nsid()` to fetch controller character device name and NSID through `NVME_GET_NSID`.
- Prints `<controller>\t<nsid>`.

Dependencies:
- `open_dev()` and `get_nsid()` from `nvmecontrol.c`.
- `comnd.h` command parser macros.

Research notes:
- The command is intentionally narrow and mostly exposes kernel namespace mapping state.
