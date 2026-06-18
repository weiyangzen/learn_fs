# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2.h

## Purpose
Defines Broadcom/LSI/Avago Fusion-MPT MPI v2.x core firmware ABI structures and constants for illumos SCSI/SAS/NVMe-capable adapter drivers. It covers MPI versioning, IOC state and register layout, request/reply descriptors, message function IDs, common IOC status codes, common request/reply headers, LUN masks, and MPI/IEEE scatter-gather element formats.

## Main Interfaces
- MPI version and header constants:
  - MPI 2.0, 2.5, and 2.6 version macros
  - `MPI2_HEADER_VERSION_UNIT` value `0x2E`
  - `MPI2_HEADER_VERSION`
- IOC state and system-interface register ABI:
  - `MPI2_SYSTEM_INTERFACE_REGS`
  - doorbell, write-sequence, host diagnostic, diagnostic read/write, interrupt, reply-free, reply-post, host-context-buffer, scratchpad, request-post, and atomic request-post offsets and masks
  - hard reset timing constants
- Request descriptors:
  - `MPI2_DEFAULT_REQUEST_DESCRIPTOR`
  - `MPI2_HIGH_PRIORITY_REQUEST_DESCRIPTOR`
  - `MPI2_SCSI_IO_REQUEST_DESCRIPTOR`
  - `MPI2_SCSI_TARGET_REQUEST_DESCRIPTOR`
  - `MPI2_RAID_ACCEL_REQUEST_DESCRIPTOR`
  - MPI 2.5 fast-path and MPI 2.6 PCIe-encapsulated aliases
  - `MPI2_REQUEST_DESCRIPTOR_UNION`
  - `MPI26_ATOMIC_REQUEST_DESCRIPTOR`
- Reply descriptors:
  - `MPI2_DEFAULT_REPLY_DESCRIPTOR`
  - `MPI2_ADDRESS_REPLY_DESCRIPTOR`
  - `MPI2_SCSI_IO_SUCCESS_REPLY_DESCRIPTOR`
  - `MPI2_TARGETASSIST_SUCCESS_REPLY_DESCRIPTOR`
  - `MPI2_TARGET_COMMAND_BUFFER_REPLY_DESCRIPTOR`
  - `MPI2_RAID_ACCELERATOR_SUCCESS_REPLY_DESCRIPTOR`
  - MPI 2.5 fast-path and MPI 2.6 PCIe-encapsulated aliases
  - `MPI2_REPLY_DESCRIPTORS_UNION`
- Message function codes for SCSI I/O, task management, IOC init/facts, config, port facts/enable, events, firmware download/upload, RAID, toolbox, enclosure processor, SMP/SATA passthrough, diagnostic operations, target command buffers, host discovery, power management, host messages, NVMe encapsulation, product-specific functions, doorbell reset, and handshake.
- Common IOC status and log-info constants for general errors, config, SCSI, EEDP, target mode, SAS SMP, diagnostic release, RAID accelerator, and log-info availability.
- Common message structures:
  - `MPI2_REQUEST_HEADER`
  - `MPI2_DEFAULT_REPLY`
  - `MPI2_VERSION_STRUCT`
  - `MPI2_VERSION_UNION`
  - shared LUN addressing masks
- MPI scatter/gather structures and helpers:
  - simple 32/64-bit SGEs
  - chain 32/64-bit SGEs
  - transaction context SGEs for 32/64/96/128-bit contexts
  - MPI SGE unions
  - SGE flags, length, chain offset, and read-modify-write helper macros
- IEEE scatter/gather structures and helpers:
  - IEEE simple 32/64-bit SGEs
  - IEEE chain SGEs for MPI 2.0 and MPI 2.5+
  - IEEE SGE unions
  - IEEE element type, next-segment-format, address-space flags, and helper macros
- Combined MPI/IEEE SGE unions and `SGLFlags` values for address space and SGL type selection.

## Dependencies And Relationships
This header assumes base MPI integer and pointer typedefs such as `U8`, `U16`, `U32`, `U64`, and `MPI2_POINTER` are available from surrounding MPI headers. It is the common low-level dependency for MPI v2 adapter message headers that define SCSI, IOC, config, RAID, SAS, and other function-specific payloads.

## Research Notes
The header identifies itself as `mpi2.h` version `02.00.46`, with history through September 2, 2016. Names prefixed `MPI25`/`Mpi25` are for MPI v2.5 products, while `MPI26` additions cover MPI v2.6 features such as scratchpad registers, atomic request descriptor posting, PCIe/NVMe encapsulation, and selected IEEE SGE next-segment formats.

## Notable Risks
- This is a firmware hardware ABI. Register offsets, descriptor sizes, flags, function IDs, and status codes must match adapter firmware exactly.
- Several SGE macros are explicitly read-modify-write operations; callers must avoid accumulating stale flags or lengths into reused descriptors.
- MPI 2.0, 2.5, and 2.6 structures coexist in one header. Driver code must choose the correct descriptor, SGE format, and feature bits for the controller generation.
- `MPI2_SYSTEM_INTERFACE_REGS` is declared `volatile`, reflecting MMIO semantics; consumers must preserve ordering and avoid treating it as ordinary memory.
