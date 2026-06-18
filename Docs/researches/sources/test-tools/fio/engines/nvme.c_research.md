# sources/test-tools/fio/engines/nvme.c

## Purpose
Provides NVMe helper logic for the `io_uring_cmd` engine. It constructs NVMe passthrough commands, discovers namespace/controller geometry and protection-information capabilities, generates and verifies PI guard/application/reference tags, implements ZNS zone callbacks, and fetches FDP reclaim unit handle status.

## Important APIs, Types, And Functions
Important exported functions are `fio_nvme_uring_cmd_prep()`, `fio_nvme_pi_fill()`, `fio_nvme_generate_guard()`, `fio_nvme_pi_verify()`, `fio_nvme_get_info()`, `fio_nvme_get_zoned_model()`, `fio_nvme_report_zones()`, `fio_nvme_reset_wp()`, `fio_nvme_get_max_open_zones()`, and `fio_nvme_iomgmt_ruhs()`. Internal helpers include 16-byte and 64-byte PI generate/verify functions, `fio_nvme_uring_cmd_trim_prep()`, `nvme_identify()`, `nvme_report_zones()`, and `nvme_fdp_reclaim_unit_handle_status()`.

## Control Flow
Command prep zeroes an `nvme_uring_cmd`, selects opcode by fio direction, builds DSM ranges for trim, flush for sync, SLBA/NLB for read/write/compare/verify/write-zeroes/write-uncorrectable, optionally points to an iovec, and attaches separate metadata when present. PI fill sets NVMe PRINFO flags, generates guard data when the controller will not insert/remove it, and populates reference/application tag command dwords. PI verification recomputes CRC-T10DIF or NVMe CRC64 and compares guard/app/ref tags per LBA. Info discovery opens the namespace char device, reads namespace id, identify controller, identify namespace, optional NVM namespace identify for ELBAS, computes LBA size/extended LBA metadata, PI type, guard type, and namespace size.

ZNS helpers identify ZNS support, report zones in chunks, translate NVMe descriptors to fio `zbd_zone`, reset zone write pointers, and read max-open-zone limits. FDP helper sends an IO management receive command and maps unsupported failures to `-ENOTSUP`.

## State And Persistence
`struct nvme_data` is stored by callers in file engine data and carries namespace id, LBA sizes, metadata size, PI type, guard type, and PI location. Helper calls can alter device state through DSM deallocate and ZNS reset operations.

## Dependencies And Integration Points
Depends on Linux NVMe ioctl UAPI, fio CRC implementations, endian helpers, fio `zbd` types, and `nvme.h` structure declarations. It is not a standalone engine; `io_uring.c` calls it for command setup, open validation, completion verification, and zoned/FDP callbacks.

## Risks
The helpers require `/dev/ngXnY` namespace generic char devices. LBA/metadata validation must match the caller's block-size checks. PI interval calculation differs for extended vs separate metadata and first/last PI placement. `fio_nvme_get_max_open_zones()` returns `mor + 1`; callers must know NVMe zero-based semantics. Some identify failures return raw ioctl errors while other paths return negative errno.

## Test Signals
Test NVM and ZNS namespace identify, unsupported file types, namespaces with no PI, 16-byte and 64-byte guards, PRACT on/off, extended and separate metadata, read/write/compare/verify/flush/trim command construction, multi-range DSM, ZNS report/reset/max-open behavior, FDP RUH fetch, and CRC mismatch error logs.
