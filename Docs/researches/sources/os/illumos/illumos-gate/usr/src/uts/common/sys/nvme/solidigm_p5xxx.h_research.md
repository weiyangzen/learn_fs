# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/solidigm_p5xxx.h

## Purpose

`nvme/solidigm_p5xxx.h` defines uncommitted vendor-specific interfaces for Intel/Solidigm P5510, P5520, and P5620 NVMe devices.

## Main Interfaces

The family shares PCI device ID `SOLIDIGM_P5XXX_DID` = `0xb60`; subsystem IDs distinguish P5510 U.2, P5520 U.2/E1.S/E1.L, and P5620 U.2 variants.

`solidigm_p5xxx_vul_t` defines log IDs for the P5510 directory, P5x20 OCP SMART, read/write latency histograms, temperature, SMART, I/O queue state, marketing description, power, garbage collection, and latency outliers.

Packed payload structures include:

- `solidigm_vul_p5xxx_lat_t`: 4876-byte read/write latency histogram with 19 groups of 64 buckets plus average latency.
- `solidigm_vul_iosq_t` and `solidigm_vul_iocq_t`: I/O submission/completion queue snapshots.
- `solidigm_vul_p5xxx_ioq_t`: 1024-byte queue log for up to 32 IOSQs and IOCQs.
- `solidigm_vul_p5x2x_power_t`: two 32-bit power readings in microwatts.
- `solidigm_vul_gc_ent_t` and `solidigm_vul_p5xxx_gc_t`: garbage-collection event log.
- `soligm_vul_lat_ent_t` and `solidigm_vul_p5xxx_lat_outlier_t`: variable-length latency outlier log.

`SOLIDIGM_VUL_MAX_QUEUES`, `SOLIDIGM_VUC_MARK_NAME_LEN`, and `SOLIDIGM_VUC_MAX_GC` define parser bounds.

## Runtime Use

Consumers must disambiguate devices by subsystem ID, select the correct log bucket, and parse fixed or variable-length payloads according to the log ID. Latency logs require prior device configuration through vendor-specific feature control to contain useful data.

## Dependencies

Includes `sys/stdint.h`, `sys/debug.h`, `sys/stddef.h`, and `sys/nvme/ocp.h`.

## Risks and Invariants

The shared device ID makes subsystem ID matching mandatory.

Latency histogram field names encode bucket ranges and widths; parser math should match the documented ranges rather than assume uniform buckets.

`soligm_vul_lat_ent_t` appears to miss the second `d` in `solidigm`, a typedef spelling inconsistency that consumers must use as written.

Variable-length outlier logs require bounds checks against returned buffer length and `lao_nents`.
