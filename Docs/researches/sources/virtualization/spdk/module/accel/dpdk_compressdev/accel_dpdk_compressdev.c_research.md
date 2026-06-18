# File Research: sources/virtualization/spdk/module/accel/dpdk_compressdev/accel_dpdk_compressdev.c

## Purpose

Implements an SPDK accel compression backend using DPDK compressdev PMDs for stateless deflate compression/decompression.

## Main Responsibilities

- Enables and registers accel module `"dpdk_compressdev"`.
- Discovers DPDK compressdev devices and configures queue pairs.
- Creates shared compression and decompression xforms.
- Maintains global device/qpair inventory and assigns one qpair per SPDK IO channel.
- Converts SPDK iovecs into DPDK mbuf chains using external buffers.
- Enqueues one DPDK compression op per SPDK accel task.
- Polls completions and completes SPDK tasks.
- Supports PMD selection: auto, QAT-only, MLX5 PCI-only, UADK-only.
- Writes config JSON for `compressdev_scan_accel_module`.

## Key Data

- PMD names:
  - `compress_qat`
  - `mlx5_pci`
  - `compress_uadk`
- `compress_dev`: DPDK device info, cdev id, shared xforms, SGL support, qpair list.
- `comp_device_qp`: unique device/qpair assignment record.
- `compress_io_channel`: selected PMD/qpair, poller, mbuf arrays, queued tasks.
- Global mempools:
  - `g_mbuf_mp`
  - `g_comp_op_mp`

## Supported Operations

- `SPDK_ACCEL_OPC_COMPRESS`
- `SPDK_ACCEL_OPC_DECOMPRESS`

## Supported Algorithms

- `SPDK_ACCEL_COMP_ALGO_DEFLATE`
- Level range reports min/max as `0/0`; hardware xform uses max deflate level by default.

## Key Control Flow

- `accel_compress_init()` optionally initializes UADK vdev, initializes all compressdevs, then registers IO device.
- `create_compress_dev()` configures a compressdev, queue pairs, starts it, creates private xforms, and records qpair objects.
- `_compress_operation()` calculates needed mbufs, attaches source/destination external buffers, checks SGL capability, sets xform, and enqueues the DPDK operation.
- `comp_dev_poller()` dequeues operations, updates output size, completes tasks, frees mbufs/op, and retries queued tasks.

## Notes / Risks

- The code uses DPDK dynamic mbuf fields to store the SPDK task pointer.
- `_setup_compress_mbuf()` splits buffers around physical-contiguity/size limits and chains mbufs.
- Channel creation picks the device with the most free qpairs for the chosen PMD.
- Module unregister destroys `g_comp_device_qp_lock`, making repeated lifecycle assumptions worth reviewing.
- Some error paths assert after failed operations, indicating expectation that normal runtime backpressure should be queued rather than fatal.
