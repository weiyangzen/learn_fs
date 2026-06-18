# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/smrt/smrt.h

This is the primary private header for the illumos `smrt` Smart Array SCSI HBA driver. It ties together controller state, logical/physical device tracking, DMA bookkeeping, command lifecycle flags, SCSA target integration, interrupt setup, discovery, controller reset, and event notification entry points.

Key definitions:
- Requires little-endian and little-to-high bitfield layout at compile time because the driver maps packed controller hardware structures directly.
- Defines global sizing constants: `SMRT_MAX_LOGDRV` as 64 and `SMRT_MAX_PHYSDEV` as 128.
- Defines controller initialization levels, controller status/discovery flags, command tag ranges, iport names, discovery and timeout constants, and HP vendor/device identifiers.
- `struct smrt` is the central per-controller soft state, containing devinfo pointers, config table mappings, SCSA target maps, mutex/condition variables, inflight/finish/abort command lists, discovered volumes/physicals, taskq/periodic handles, interrupt handles, DMA attributes, heartbeat/reset timestamps, and async event command state.
- `smrt_volume_t`, `smrt_physical_t`, and `smrt_target_t` model logical volumes, physical devices, and SCSA targets.
- `smrt_command_t` tracks controller command tags, type/status flags, target/controller ownership, AVL/list membership, submit/complete/expiry timestamps, abort metadata, optional SCSA/internal payloads, and DMA-backed CISS command/error buffers.
- Declares the driver’s main internal API for transport submission, interrupts, controller init/reset, discovery, SCSA HBA setup, command allocation/reuse, CISS message construction, device MMIO access, SATA WWN probing, and async event handling.

Dependencies:
- Includes the CISS and Smart Array SCSI wire-format headers: `smrt_ciss.h` and `smrt_scsi.h`.
- Depends heavily on illumos kernel DDI/SCSA types, list/AVL primitives, task queues, periodic callbacks, DMA handles, and SCSI packet/device types.

Impact:
- This header is the main contract between all `smrt` driver implementation files.
- Changes here can affect command lifetime, reset behavior, hotplug discovery, panic-time behavior, and target exposure.

Cautions:
- Command status flags encode subtle lifecycle states: polled completion, abandoned commands, reset-sent commands, abort-sent commands, and commands allowed while the controller is not fully running.
- Most controller state is protected by `smrt_mutex`; users must preserve the locking expectations described in comments.
- Hardware layout and bitfield ordering assumptions are explicit and non-portable outside little-endian systems.
