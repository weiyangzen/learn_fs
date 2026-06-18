# File Research: sources/virtualization/spdk/lib/nvme/nvme_ns_cmd.c

This file implements namespace I/O command construction and submission for reads, writes, compares, zone append, write zeroes, verify, write uncorrectable, dataset management, copy, flush, reservations, and I/O management send/receive. It supports contiguous buffers, callback-driven SGLs, iovec payloads, metadata buffers, protection information tags, and extended I/O options.

The core helpers compute transfer sizing and splitting. PRACT with extended LBA, PI, and 8-byte metadata can exclude metadata from host transfer size. `_nvme_get_host_buffer_sector_size()` and `_nvme_get_sectors_per_max_io()` choose sector sizing with or without metadata based on that rule. `nvme_ns_map_failure_rc()` maps allocation failures to `-EINVAL` when the requested I/O would need too many child requests for queue depth.

Requests are initialized through `_nvme_ns_cmd_rw_req_init_contig()`, `_nvme_ns_cmd_rw_req_init_sgl()`, and `_nvme_ns_cmd_rw_req_init_iov()`, each filling payload size, metadata size, offsets, callback state, and optional accel sequence. `_is_io_flags_valid()` enforces `SPDK_NVME_IO_FLAGS_VALID_MASK`, and `_is_accel_sequence_valid()` allows accel sequences only when the controller supports them and the qpair is in a poll group.

`_nvme_ns_cmd_setup_request()` fills common read/write/compare/append command fields: opcode, NSID, SLBA in CDW10/11, PI reference tag for type 1/2, fused-operation bits, NLB and CDW12 flags, CDW13, and application tag mask/tag in CDW15.

`_nvme_ns_cmd_rw()` decides whether to submit as a single request or split. It splits across namespace stripe boundaries, maximum transfer size, PRP page-alignment constraints, SGL max-SGE constraints, and iovec max-SGE constraints. Split requests are represented by parent/child `nvme_request` objects; child completions aggregate into the parent. Splitting with accel sequences is explicitly unsupported and fails. If no split is required, the original request is configured directly.

PRP splitting validates that child SGL segments start and end on controller page boundaries except for first and last child positions. SGL splitting limits children by `ctrlr->max_sges`, trimming child length to LBA boundaries when an SGE crosses a block boundary. IOV variants perform the same logic using `spdk_iov_sgl`.

Read, write, and compare public APIs are repetitive wrappers around the core path. Each validates flags, validates SGL callbacks where applicable, allocates the right payload type, calls `_nvme_ns_cmd_rw()` with the opcode and metadata/tag options, maps failures, and submits. Extended variants read optional fields from `struct spdk_nvme_ns_cmd_ext_io_opts` using the ABI-safe macro from `nvme_internal.h`, attach metadata, CDW13, protection tags, and accel sequence when supplied. IOV calls with one element collapse to contiguous payloads.

Zone append has stricter handling. `nvme_ns_cmd_check_zone_append()` requires controller zone-append support and rejects payloads larger than `ctrlr->max_zone_append_size`. The append builders still call `_nvme_ns_cmd_rw()` to validate SGL/PRP constraints, but they assert and enforce that no child requests are produced because zone append commands cannot be split.

Non-read/write commands are direct builders. Write Zeroes and Verify require `1 <= lba_count <= UINT16_MAX + 1` and fill normal LBA/count fields. Write Uncorrectable has the same count range and no payload. Dataset Management validates range count and range pointer, copies DSM ranges as host-to-controller payload, sets NR and type. Copy validates source ranges, copies them as payload, sets destination LBA and range count. Flush is a no-payload NSID command.

Reservation helpers build Register, Release, Acquire, and Report commands. Register/Release/Acquire use user-copy payloads and encode action, ignore-key, cptpl, and reservation type bits. Report requires DWORD-aligned length, sets zero-based DWORD count, and enables extended data when the controller selected 128-bit Host Identifier support. I/O Management Receive requires DWORD-aligned length and sets management operation/suboperation plus transfer count; Send copies the payload and sets operation fields.

Key invariants are child request lifetime, parent completion aggregation, correct payload/metadata offsets during splitting, zone append no-split enforcement, extended option size checks, and consistent error mapping when an I/O cannot be represented within queue/request limits.
