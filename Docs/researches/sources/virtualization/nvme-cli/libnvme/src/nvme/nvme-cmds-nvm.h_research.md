# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-nvm.h

## Role

Inline helper header for NVM Command Set I/O command initialization and related payload builders.

## Command Initializers

- `nvme_init_flush()`: flush command.
- `nvme_init_io()`: generic I/O initializer for opcode, namespace, SLBA, data, and metadata buffers.
- `nvme_init_write()`, `nvme_init_read()`: read/write setup with NLB, control, DSM/CEV, directive-specific fields.
- `nvme_init_write_uncorrectable()`: no-transfer write uncorrectable.
- `nvme_init_compare()`: compare setup.
- `nvme_init_write_zeros()`: no-transfer write zeroes.
- `nvme_init_dsm()`: dataset management command.
- `nvme_init_verify()`: verify command.
- Reservation helpers:
  - `nvme_init_resv_register()`
  - `nvme_init_resv_report()`
  - `nvme_init_resv_acquire()`
  - `nvme_init_resv_release()`
- I/O management helpers:
  - `nvme_init_io_mgmt_recv()`
  - `nvme_init_fdp_reclaim_unit_handle_status()`
  - `nvme_init_io_mgmt_send()`
  - `nvme_init_fdp_reclaim_unit_handle_update()`
- `nvme_init_copy()`: copy command setup, selecting data length by copy descriptor format.

## Payload/Field Builders

- `nvme_init_app_tag()`: encodes logical block application tag and mask into `cdw15`.
- `nvme_init_dsm_range()`: fills DSM range descriptors with endian conversion.
- `nvme_init_copy_range_f0/f1/f2/f3()`: fills copy range descriptor formats, including source namespace and expected tag fields.
- `nvme_init_var_size_tags()`: encodes variable-sized protection/storage tags into `cdw2`, `cdw3`, and `cdw14` for 16B, 32B, or 64B guard formats.

## Validation

- Most helpers encode caller-provided values directly.
- `nvme_init_var_size_tags()` returns `-EINVAL` for unsupported protection information format.
- Several helpers use one-based command conventions by encoding `nr - 1` or `npids - 1`; callers must avoid passing zero where invalid.

## Dependencies

Includes `errno.h`, `string.h`, `nvme/endian.h`, `nvme/ioctl.h`, `nvme/nvme-types-nvm.h`, and `nvme/nvme-cmds-base.h`.

## Notes

This header is command-construction only. It does not perform I/O size validation against namespace geometry or controller capabilities.
