# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-base.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-6562, source bytes 262080, report `Docs/researches/chunks/chunk_sources_virtualization_nvme_cli_libnvme_src_nvme_nvme_types_base_h_1_1_6_d45d3742de5a_research.md`
- chunk 2: lines 6563-9212, source bytes 102754, report `Docs/researches/chunks/chunk_sources_virtualization_nvme_cli_libnvme_src_nvme_nvme_types_base_h_2_656_fd02d2e04a63_research.md`

## Chunk Research

### Chunk 1: lines 1-6562

# Chunk Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-base.h lines 1-6562

## Scope

This chunk is the first 6,562 lines of `libnvme`'s NVMe base-specification type header. It is in subset A because `sources/virtualization/nvme-cli` is part of the virtualization/block-device integration source trees in `Docs/research_subset_a.md`.

The chunk is declaration-heavy C API surface: constants, bitfield helpers, controller register layouts, Identify data structures, log page structures, feature payloads, asynchronous event codes, and the beginning of status-code documentation. There is almost no runtime control flow beyond four small inline helpers.

## APIs and Declarations

### Public bitfield helper API

- Lines 40-41 define UUID sizing constants.
- Lines 54-107 define the central field extraction and construction macros:
  - `NVME_GET(value, name)` and `NVMF_GET(value, name)` extract fields using `*_SHIFT` and `*_MASK`.
  - `NVME_SET(value, name)` and `NVMF_SET(value, name)` build shifted field values after masking to `__u32`.
  - `NVME_CHECK(value, name, check)` compares a value to an enum constant.
  - `NVME_VAL(name)` produces shifted masks and is reused by many flag enums.

These macros are the foundation for nearly every `NVME_*()` accessor macro in this chunk.

### Global NVMe constants and command-set IDs

- `enum nvme_constants` at lines 161-192 defines sentinel IDs and fixed transfer/list limits: `NVME_NSID_ALL`, `NVME_NSID_NONE`, omit-value sentinels, identify transfer size `4096`, list maximums, telemetry block size `512`, namespace/NQN/fabrics address limits, and ZNS/stream limits.
- `enum nvme_csi` at lines 202-208 declares command set indicators for NVM, KV, ZNS, subsystem local memory, and computational programs.

### Controller register model

- `enum nvme_register_offsets` at lines 243-272 maps controller BAR0/property offsets for CAP, VS, INTMS/INTMC, CC, CSTS, queue registers, CMB, boot partition, CRTO, and PMR registers.
- `nvme_is_64bit_reg(__u32 offset)` at lines 286-298 classifies `CAP`, `ASQ`, `ACQ`, `BPMBL`, and `CMBMSC` as 64-bit registers. This helper intentionally ignores transport support and only identifies width by offset.
- Register bitfield enums and accessor macros cover:
  - CAP at lines 344-402.
  - VS at lines 413-428.
  - CC at lines 460-497.
  - CSTS at lines 517-540.
  - AQA/ASQ/ACQ at lines 549-579.
  - CMB location/size/control/status/elasticity/throughput at lines 600-858.
  - Boot partition registers at lines 709-757.
  - CRTO at lines 868-876.
  - PMR capabilities/control/status/size/throughput/memory-space control at lines 899-1062.
- `nvme_cmb_size(__u32 cmbsz)` at lines 690-694 computes CMB bytes from `CMBSZ.SZ` and `CMBSZ.SZU`.
- `nvme_pmr_size(__u32 pmrebs)` at lines 1005-1009 computes PMR bytes from `PMREBS.PMRSZ` and `PMREBS.PMRSZU`.
- `nvme_pmr_throughput(__u32 pmrswtp)` at lines 1042-1046 computes PMR throughput units from `PMRSWTP`.

### Power and LBA format primitives

- `enum nvme_unit` at lines 799-804 supplies unit exponents used by CMB/PMR helper-style fields.
- FLBAS and power descriptor support appears at lines 1073-1250:
  - `enum nvme_flbas`, `enum nvme_psd_flags`, `enum nvme_psd_ps`, `enum nvme_power_measurement_type`, `enum nvme_power_measurement_action`, `enum nvme_psd_workload`.
  - `nvme_psd_power_scale(__u8 ps)` at lines 1150-1153 extracts the upper three bits of a power scale byte.
  - `struct nvme_id_psd` at lines 1229-1250 models one Identify Controller power-state descriptor.

### Identify Controller API surface

- `struct nvme_id_ctrl` at lines 1548-1677 is the 4096-byte Identify Controller payload model. It contains:
  - PCI/vendor identity strings and IDs.
  - controller version, retry delays, capabilities, async event support, controller attributes, boot partition, power-loss signaling, reachability, controller type, FRU GUID, admin capabilities, thermal management, sanitize, HMB, NVM set/endurance group, ANA, persistent event log, power measurement, queue sizes, namespace limits, NVM command capabilities, SGLs, tracking and migration limits, fabrics-only fields, 32 power descriptors, and vendor-specific space.
- Controller capability enums and accessors follow the struct:
  - CMIC at lines 1692-1737.
  - OAES at lines 1787-1837.
  - CTRATT at lines 1866-1889.
  - BPCAP, PLSI, CRCAP, controller/discovery type, NVMSR, VWCI, MEC at lines 1912-2040.
  - OACS at lines 2096-2146.
  - FRMW, LPA, AVSCC, APSTA, RPMBS, DSTO, HCTM, SANICAP, ANACAP, KPIOC, CDPA, IPMSR, SQES, CQES, ONCS, FUSES, FNA, VWC, NVSCC, NWPC, SGLS, TRATTR, FCATT, and OFCS at lines 2160-2659.

### Identify Namespace and identify-list API surface

- `struct nvme_lbaf` and `enum nvme_lbaf_rp` at lines 2669-2693 define LBA format descriptors and performance rankings.
- `struct nvme_id_ns` at lines 2801-2845 models the Identify Namespace data payload: sizes/capacity/use counters, format and metadata fields, protection settings, reservations, deallocation behavior, atomic and copy geometry, key-per-I/O, ANA group, NVM set/endurance group, NGUID/EUI64, 64 LBA formats, and vendor-specific bytes.
- Namespace feature enums and accessors cover:
  - `nvme_id_nsfeat`, `nvme_id_ns_flbas`, `nvme_id_ns_mc`, `nvme_id_ns_dpc`, `nvme_id_ns_dps`, `nvme_id_ns_nmic`, `nvme_id_ns_rescap`, `nvme_nd_ns_fpi`, `nvme_id_ns_dlfeat`, and `nvme_id_ns_attr` at lines 2869-3064.
- Variable namespace identifier descriptor APIs:
  - `struct nvme_ns_id_desc` at lines 3076-3081 is packed and ends with flexible `nid[]`.
  - NID type and length enums at lines 3093-3112 define EUI64, NGUID, UUID, and CSI descriptor sizes.
- Identify-list structures at lines 3128-3448 cover NVM set lists, independent namespace identify data, namespace granularity, UUID list, controller list, namespace list, NVM-command-set-specific identify controller data, primary/secondary controller capabilities, I/O command set vectors, domain list, endurance group list, and supported log pages.

### Log page and event payload API surface

- Error log:
  - `struct nvme_error_log_page` at lines 3518-3534.
  - `enum nvme_err_pel`, `enum nvme_err_status_field`, and accessors at lines 3541-3563.
- SMART/health:
  - `struct nvme_smart_log` at lines 3736-3764.
  - SMART critical-warning enums and accessors at lines 3823-3868.
- Firmware, command effects, and self-test:
  - `struct nvme_firmware_slot` at lines 3877-3882.
  - `struct nvme_cmd_effects_log`, `enum nvme_cmd_effects`, and accessors at lines 3890-3921.
  - Packed `struct nvme_st_result`, self-test result/code/current-operation enums, valid diagnostic info, and packed `struct nvme_self_test_log` at lines 3962-4114.
- Telemetry and endurance:
  - Telemetry LSP/DA enums and `struct nvme_telemetry_log` at lines 4121-4202; the log header ends in flexible `data_area[]`.
  - `struct nvme_endurance_group_log` and critical-warning flags at lines 4226-4260.
  - Aggregate endurance and predictable latency logs at lines 4267-4346.
- ANA and persistent events:
  - ANA group/log structures and state enum at lines 4357-4394.
  - Packed persistent event log header, reporting-context fields, persistent event entry, event type enum, event header additional info, vendor-specific event descriptor, firmware commit event, timestamp-change event, reset info, and namespace/format/sanitize/set-feature/thermal event records at lines 4418-4815.
- LBA status and feature effects:
  - LBA range/status structures and action enum at lines 4823-4876.
  - Endurance event aggregate log at lines 4883-4886.
  - Feature Identifier Supported and Effects enum/log at lines 4906-4933.
- Miscellaneous log pages:
  - Boot partition, rotational media, dispersed namespace participation, management address list, PCIe eye opening measurement, reachability groups/associations, media unit status/configuration, capacity configuration, lockdown log, sanitize status, power histogram/timestamp/power measurement, LBA status descriptors, APST, performance characteristics, host metadata, LBA range type, predictable latency mode config, host behavior, streams directives, identify directives, HMB attributes, asynchronous event values, and pull-model DDC request log are declared from lines 4945-6263.

### Status-code documentation starts but does not complete

- Lines 6264-6562 begin the documentation block for `enum nvme_status_field`. Within this chunk only the comment is visible; the actual enum declaration and most numeric status definitions continue in the next chunk.
- The visible documentation covers the field layout concept (`SCT`, `SC`, masks/shifts) and many generic, media, path, KV, queue, firmware, feature, namespace-management, sanitize, and FDP status meanings, but definitions are not yet present in this chunk.

## Control Flow

There is no command execution, I/O, allocation, or mutable control loop in this chunk. Control flow consists only of:

- `nvme_is_64bit_reg()` switch dispatching known register offsets to true and all others to false.
- `nvme_cmb_size()` arithmetic from CMB size fields.
- `nvme_pmr_size()` arithmetic from PMR size fields.
- `nvme_pmr_throughput()` arithmetic from PMR sustained-write-throughput fields.
- `nvme_psd_power_scale()` shifting a byte right by six.

All other behavior is compile-time structure layout and preprocessor macro expansion.

## State and Data Model

The chunk models host-visible NVMe device state rather than maintaining library state:

- Controller register state: CAP, VS, CC, CSTS, queue base addresses, CMB/PMR/boot-partition registers, and controller-ready timeout fields.
- Identify state: controller capabilities, namespace geometry, namespace formats, controller/namespace/domain/endurance lists, and command-set support.
- Health and telemetry state: SMART counters, endurance group health, telemetry logs, persistent events, sanitize state, power measurements, LBA status, EOM, reachability, and media unit configuration.
- Feature state payloads: APST, host metadata, LBA range type, predictable latency mode, host behavior, streams directive, identify directives, and HMB attributes.
- Asynchronous event taxonomy: event type and event information enums for error, SMART, notices, CSS/NVM events, and vendor-specific events.

Data representation is wire-format oriented:

- Fixed-width NVMe/Linux-style typedefs from `nvme/types.h` are used throughout.
- Little-endian fields use `__le16`, `__le32`, and `__le64`.
- 128-bit quantities are represented as `__u8[16]`, not native integers.
- Reserved fields are explicit padding arrays, preserving spec offsets.
- Several payloads are variable length through C99 flexible array members, and a few use legacy zero-length arrays.
- Some records are explicitly `__attribute__((packed))`, mostly where the wire layout would otherwise be compiler-aligned differently.

## Dependencies

- Standard headers: `<stdbool.h>`, `<stdint.h>`, and `<stdio.h>` at lines 14-16.
- Local/libnvme dependency: `<nvme/types.h>` at line 18. This supplies `__u8`, `__le16`, `__le32`, `__le64`, and related NVMe endian/fixed-width aliases.
- Later chunks in the same file provide status-field definitions, command structures, command opcode definitions, feature identifiers, and likely additional helper macros referenced by comments or by fields in this chunk.
- Many comments reference NVMe base-spec concepts and structs/enums declared later or elsewhere, including `nvme_trtype`, `nvme_status_field`, `NVME_FEAT_FID_*`, `NVME_LOG_LID_*`, command-specific CDW layouts, and fabrics/discovery constructs.

## Risks and Edge Cases

- Macro correctness is critical because most field accessors expand through `NVME_GET`. A typo in a macro name or missing shift/mask breaks compile-time consumers rather than causing a local runtime failure.
- Several accessor macros in this chunk appear suspicious from local evidence:
  - Line 1034 defines `NVME_PMRSWTP_PMRSWTV(pmrswtp)` using `PMRSWTP_PMRSWTU`, so it extracts the unit field instead of the value field.
  - Line 1965 defines `NVME_CTRL_CRCAP_RGICS(crcap)` using `CTRL_CRCAP_RGICS`, but the enum at lines 1957-1962 defines `RGIDC`, not `RGICS`.
  - Lines 2135-2146 define `NVME_CTRL_OACS_*` macros that call `NVME_GET(CTRL_OACS_...)` without passing the `oacs` value argument. As written, these expand to the wrong arity for `NVME_GET`.
- `NVME_SET()` and `NVMF_SET()` cast the value to `__u32`; this is suitable for many dword fields but is risky if reused for wider fields. Several 64-bit masks are modeled as `static const __u64` rather than enum constants, suggesting width sensitivity in this header.
- `nvme_cmb_size()`, `nvme_pmr_size()`, and `nvme_pmr_throughput()` trust the encoded unit fields. If future specs assign unit values that shift by large amounts, callers depend on valid register contents to avoid nonsensical sizes. Current masks bound the shifts in this chunk.
- Flexible and zero-length array payloads require callers to validate external log lengths before indexing. Relevant examples include namespace ID descriptors, telemetry data, ANA descriptors, persistent event follow-on data, LBA status elements, EOM descriptors, reachability descriptors, capacity config descriptors, power measurement descriptors, performance/metadata arrays, stream status IDs, and pull-model DDC parameters.
- `struct nvme_nss_hw_err_event` at lines 4675-4679 contains `__u8 *add_hw_err_info`; unlike most declarations here, that is a host pointer, not an inline wire-format flexible buffer. Serializing or overlaying raw persistent-event data directly onto this struct would be unsafe or non-portable.
- Some variable records use nested flexible arrays (`nvme_supported_cap_config_list_log` -> `nvme_capacity_config_desc` -> `nvme_end_grp_config_desc`, and media unit/channel/endurance config descriptors). Consumers need parser logic based on count and length fields, not `sizeof`.
- Packed structs protect wire layout but can create unaligned member accesses on strict-alignment architectures if consumers dereference little-endian integer members directly from raw buffers.
- The chunk uses compiler extensions: `__attribute__((packed))` and zero-length arrays. This is normal for GNU C/libnvme-style headers but constrains portability to compilers that accept these extensions.
- Comments reference several feature IDs and log IDs not defined in this chunk. Documentation generation may resolve them only when the full header or full libnvme include graph is loaded.

## Cross-Chunk References

- The file continues beyond line 6562. This chunk ends in the documentation block for `enum nvme_status_field`; the enum declaration and numeric status definitions are expected in chunk 2.
- Command, feature, and status-code definitions after line 6562 likely consume the constants and structures declared here. In particular, status-code masks/shifts documented at the end of this chunk are incomplete until the next chunk is read.
- The structs declared here are likely used by libnvme command wrappers and nvme-cli commands outside this header to size buffers for Identify, Get Log Page, Get/Set Features, telemetry, sanitize, and event-log operations.
- The accessors and constants in this chunk establish naming conventions (`NVME_<FIELD>_SHIFT`, `NVME_<FIELD>_MASK`, `NVME_<GROUP>_<FIELD>(value)`) that later chunks should follow for command CDW fields and status decoding.

## Research Notes

- Read scope: `Docs/research_subset_a.md`.
- Read source range completely: `sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-base.h` lines 1-6562.
- Did not create or modify the final per-file report `Docs/researches/sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-base.h_research.md`.

### Chunk 2: lines 6563-9212

# Chunk Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-base.h lines 6563-9212

## Scope

This report covers only `sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-base.h` lines 6563-9212 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely. Adjacent context was used only to identify the file-level contract (`NVMe Base Specification type definitions`, based on NVMe Base Specification 2.3) and the shared bitfield helpers `NVME_GET()` / `NVME_SET()`.

This chunk starts inside the documentation block for `enum nvme_status_field` and runs through the end of the file.

## APIs And Type Surface

The chunk is a public C header surface for libnvme's base NVMe constants, packed wire-layout structures, and inline decode helpers:

- Status API: `enum nvme_status_field` defines status code type bits, status code masks, generic status codes, command-specific status codes, command-set-specific status codes, media/data-integrity errors, path errors, and status flags (`CRD`, `MORE`, `DNR`) at lines 6774-6995. `nvme_status_code_type()` and `nvme_status_code()` extract SCT and SC from a completion status field at lines 7004-7019.
- API return status encoding: `enum nvme_status_type` reserves high bits in positive `int` returns for NVMe vs NVMe-MI status types at lines 7040-7046. `NVME_STATUS_TYPE()`, `nvme_status_get_type()`, `nvme_status_get_value()`, and `nvme_status_equals()` expose the type/value split at lines 7048-7090.
- Command and selector constants: `enum nvme_admin_opcode` covers admin opcodes, including Identify, Features, namespace management, virtualization, discovery, live migration, fabrics, format, security, sanitize, and memory-range commands at lines 7145-7196. `enum nvme_identify_cns`, `enum nvme_cmd_get_log_lid`, and `enum nvme_features_id` map Identify CNS values, log page identifiers, and feature identifiers at lines 7245-7472.
- Feature bitfield definitions: `enum nvme_feat` defines the `_SHIFT` and `_MASK` constants consumed by `NVME_GET()` / `NVME_SET()` for arbitration, power management, LBA range, temperature thresholds, error recovery, volatile write cache, queue counts, interrupt settings, async events, APST, HMB, HCTM, predictable latency, LBA status, sanitize, endurance group events, FDP, host ID, reservations, write protection, performance characteristics, power limit, power threshold, and power measurement at lines 7649-7822.
- Command subfield enums: lines 7831-8369 define small value enums for Get Features `SEL`, Format NVM metadata/protection/erase settings, namespace management and attachment selections, firmware commit actions, directives, sanitize actions, device self-test actions, virtualization management, namespace write-protect states, ANA log selection, PHY RX EOM action/quality, persistent event log action, async event flags, PLM window selection, performance characteristic buckets, fabrics command types, NVM I/O opcodes, and key-value opcodes.
- Namespace management data: `struct nvme_ns_mgmt_host_sw_specified` at lines 8426-8454 is a SWIG-hidden wire-layout structure for host-specified namespace creation data, including namespace size/capacity, FLBAS/DPS/NMIC, ANA group, NVM set/endurance group, logical block storage tag mask, FDP placement handles, and an overlaid ZNS-specific area.
- Live migration support: lines 8483-8901 define Controller Data Queue, Track Send, Migration Send, and Migration Receive command-field masks plus live-migration controller state structures for submission/completion queue state and controller state payloads.
- Feature decode helpers: lines 8903-9202 expose `NVME_FEAT_*` getter macros and `static inline` `nvme_feature_decode_*()` functions for common feature result dwords. The chunk ends with `nvme_id_ns_flbas_to_lbaf_inuse()` at lines 9207-9212, combining the lower and higher FLBAS format-index bits.

## Control Flow

There is no runtime control flow beyond inline extraction helpers. The only branch in the chunk is `nvme_status_equals()` checking negative API return values before comparing encoded positive status type/value fields at lines 7082-7090.

All other inline functions are straight-line pointer-output decoders from a `__u32` value or an `__u8` FLBAS byte. They do not allocate, perform I/O, lock, mutate globals, validate pointers, or convert little-endian wire fields.

## State And Dependencies

The chunk defines immutable compile-time constants and C struct layouts. Runtime state is caller-owned: callers pass status integers, command dwords, or pointers to output variables; helpers only write through those pointers.

Direct dependencies visible in or adjacent to this chunk are:

- `NVME_GET()` and `NVME_SET()` from the file's helper macro section, which require each field name to have matching `NVME_<name>_SHIFT` and `NVME_<name>_MASK` constants.
- fixed-width and endian typedefs such as `__u8`, `__u16`, `__u32`, `__le16`, `__le32`, and `__le64` from `<nvme/types.h>`.
- `bool` from `<stdbool.h>`.
- earlier file constants such as `NVME_SMART_CRIT_*` for async event config aliases and `NVME_FLBAS_LOWER()` / `NVME_FLBAS_HIGHER()` for `nvme_id_ns_flbas_to_lbaf_inuse()`.
- downstream command builders in `nvme-cmds-base.h` and validators in `nvme-cmds.c`, which use the feature IDs, live-migration masks, namespace-management structure, and decode helpers.

## Risks And Invariants

The main risk is ABI and protocol drift. These values mirror NVMe specification numeric assignments; changing enum values, masks, shifts, field widths, reserved padding, or struct ordering changes command dwords or wire data layouts.

Status constants intentionally reuse numeric status-code values across different status code types. Consumers must compare both SCT and SC, or use the encoded libnvme status helpers, instead of treating the raw status code as globally unique.

The status-return encoding stores a type tag in high bits of a positive signed `int`; callers must not pass negative syscall/library errors into `nvme_status_get_type()` or `nvme_status_get_value()` without first checking sign. `nvme_status_equals()` handles that guard.

Most decode helpers blindly dereference output pointers. They assume non-NULL pointers and host-endian feature dword inputs. The wire structs use `__le*` fields but these helpers do not perform byte swapping.

The live-migration controller state structures use zero-length arrays in a union (`sqs[0]`, `cqs[0]`) and size fields expressed in dwords/queue counts. Consumers must compute payload offsets and sizes exactly; treating the union as containing both arrays at the same address would corrupt parsing.

`struct nvme_ns_mgmt_host_sw_specified` is hidden from SWIG and contains reserved padding plus a packed nested ZNS overlay. Layout compatibility depends on compiler support for anonymous unions and `__attribute__((packed))`.

There are minor spelling/API-stability quirks visible in public names (`NVME_SC_INVALID_CONTROLER_DATA_QUEUE`, `nvme_feature_decode_reservation_persistance`). They should be treated as stable exported identifiers despite spelling.

## Cross-Chunk References

The chunk begins mid-documentation for `enum nvme_status_field`; the start of that comment and earlier status-code context are in the previous chunk. Earlier chunks also define the file-level helper macros, Identify namespace bitfield helpers, SMART critical warning bits, and the `nvme_id_ns_flbas` FLBAS masks consumed here.

This chunk reaches the end of `nvme-types-base.h`, so there is no later chunk for this file. The final per-file report should merge this public constant/helper surface with earlier chunks that define the underlying controller, namespace, log, command, and feature data structures.
