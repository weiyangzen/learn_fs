# File Research: sources/virtualization/spdk/module/accel/dsa/accel_dsa.c

## Purpose

Implements an SPDK accel backend for Intel DSA/IDXD devices.

## Main Responsibilities

- Registers accel module `"dsa"` after startup RPC enablement.
- Configures IDXD mode as kernel or user mode.
- Probes DSA devices and creates per-thread IDXD channels.
- Selects devices round-robin, constrained to the current core's NUMA socket.
- Submits copy, fill, dualcast, compare, CRC32C, copy+CRC32C, DIF, and DIX operations.
- Handles DSA busy backpressure through a queued task list.
- Uses iobuf for temporary DIX verify metadata generation.
- Registers DSA tracepoints for submit/complete counts.
- Writes config JSON for `dsa_scan_accel_module`.

## Supported Operations

- Always:
  - `COPY`
  - `FILL`
  - `DUALCAST`
  - `COMPARE`
  - `CRC32C`
  - `COPY_CRC32C`
- Only when IOMMU is enabled:
  - `DIF_VERIFY`
  - `DIF_GENERATE_COPY`
  - `DIF_VERIFY_COPY`
  - `DIX_GENERATE`
  - `DIX_VERIFY`

## Key Control Flow

- `accel_dsa_enable_probe(kernel_mode)` calls `spdk_idxd_set_config`, adds the module, and records mode.
- `accel_dsa_init()` probes DSA devices, registers iobuf module, then registers IO device.
- `_process_single_task()` maps SPDK accel opcodes to `spdk_idxd_submit_*` functions.
- `dsa_submit_task()` queues work when the IDXD channel is busy.
- `idxd_poll()` processes completions and retries queued tasks.
- `dsa_done()` completes SPDK tasks and performs software DIF detail verification if hardware returns `-EIO`.

## Notes / Risks

- The device selector requires a DSA device on the current NUMA socket; otherwise channel creation fails.
- DIX verify is implemented as DIX generate to temporary metadata plus `memcmp`, because DSA lacks a direct DIX verify operation.
- DIF strip overlap has a software fallback for a documented DSA overlap false-positive case.
