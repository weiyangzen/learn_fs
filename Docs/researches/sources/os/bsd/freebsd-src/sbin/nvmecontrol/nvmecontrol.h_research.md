# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nvmecontrol.h

Purpose: Shared public header for `nvmecontrol` command implementations and modules.

Key contents:
- Defines `struct logpage_function` and `NVME_LOGPAGE()` constructor macro for registering log-page decoders.
- Defines `DEFAULT_SIZE`, `struct kv_name`, and generic `letoh()` conversion macro.
- Declares command-shared helpers: device opening, namespace lookup, identify reads, active namespace reads, hex printing, namespace printing, log-page reading, temperature printing, Intel SMART printing, and key lookup.
- Defines portable `uint128_t` support using C23 `_BitInt(128)`, compiler `__uint128_t`, or `uint64_t` fallback.
- Defines `to128()` to decode 16-byte little-endian counters.
- Declares `le48dec()` and `uint128_to_str()`.

Dependencies:
- `<dev/nvme/nvme.h>`.
- `comnd.h`.

Research notes:
- This header is the main ABI between core commands, built-in subcommands, and vendor modules.
- `NVME_LOGPAGE()` uses constructor registration, so log pages can be added by linking or loading modules.
