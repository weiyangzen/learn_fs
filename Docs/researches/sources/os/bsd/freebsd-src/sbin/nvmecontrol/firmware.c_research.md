# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/firmware.c

Implements `nvmecontrol firmware` for firmware image download and activation.

Key behaviors:
- Options include `--firmware`, `--slot`, and `--activate`.
- Validates slot range, required action, controller firmware support, slot read-only status, and slot count.
- Reads firmware image into memory with maximum size bounded by `INT32_MAX`.
- Downloads firmware in chunks based on controller max transfer size and FWUG granularity.
- Sends `FIRMWARE_IMAGE_DOWNLOAD` and `FIRMWARE_ACTIVATE` passthrough commands.
- Checks for reset-required activation status.
- Prompts the user for explicit `yes`/`no` confirmation before dangerous actions.

Research notes:
- Firmware changes are intentionally interactive and guarded.
- Assumes full file read after one `read()` and treats short reads as fatal.
