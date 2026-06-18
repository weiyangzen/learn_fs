# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/intel/intel.c

Vendor-specific Intel NVMe log-page formatter module.

Key behaviors:
- Formats Intel temperature statistics log.
- Formats Intel read and write latency histogram logs.
- Formats Intel additional SMART data log using key/value decoding and special handling for wear leveling, media wear, temperature, power, thermal throttle, and raw counters.
- Formats Intel drive marketing name log.
- Registers log pages via `NVME_LOGPAGE` for vendor name `"intel"`.

Research notes:
- Comments note that some SMART keys are shared by Samsung/Micron but may have model-specific meanings.
- Uses little-endian decode helpers for packed vendor log buffers.
