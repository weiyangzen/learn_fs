# sources/test-tools/fio/engines/nvme.h

## Purpose
Declares NVMe UAPI-compatible structures, constants, helper inline functions, and public helper prototypes used by fio's `io_uring_cmd` NVMe implementation. It provides local fallback definitions for `nvme_uring_cmd` when system headers lack them.

## Important APIs, Types, And Functions
Key declarations include `struct nvme_uring_cmd`, NVMe passthrough ioctl constants, identify CNS/CSI/admin/io opcode enums, PI constants, ZNS state/type constants, FDP RUH structures, DSM range structures, `struct nvme_data`, `struct nvme_pi_data`, `struct nvme_cmd_ext_io_opts`, identify namespace/controller structs, and ZNS descriptor/report structs. Inline helpers are `ilog2()`, `put_unaligned_be48()`, `get_unaligned_be48()`, `fio_nvme_pi_ref_escape()`, `get_slba()`, and `get_nlb()`.

## Control Flow
As a header, it does not own runtime control flow. The inline helpers convert byte offsets and lengths into NVMe logical block numbers using either extended-LBA byte size or `lba_shift`, encode/decode 48-bit reference tags, and detect PI reference escape patterns.

## State And Persistence
The important state carrier is `struct nvme_data`, which is populated by `nvme.c` and stored in fio file engine data by `io_uring.c`. Other structs mirror device command/identify wire formats and do not own lifetime.

## Dependencies And Integration Points
Depends on `<linux/nvme_ioctl.h>` and fio core types. It is included by `io_uring.c` and `nvme.c`, binding the `io_uring_cmd` engine to local NVMe command construction and zoned/FDP helper APIs.

## Risks
Many structures mirror kernel/NVMe specification layout; padding, endian annotations, and field sizes must stay compatible with ioctl expectations. The fallback `nvme_uring_cmd` must match kernel UAPI when headers are old. `get_nlb()` returns zero-based NLB for read/write but callers adjust DSM trim to one-based ranges.

## Test Signals
Compile against old and new kernel headers, validate command struct sizes used by ioctls, exercise inline SLBA/NLB conversion with extended and non-extended LBAs, 48-bit tag encode/decode, PI reference escape handling, and all exported prototypes through `nvme.c`/`io_uring.c` builds.
