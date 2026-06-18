# File Research: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-utils.h

## Role

`sandisk-utils.h` is the constant, structure, and function declaration header for the Sandisk plugin utility layer. It encodes supported vendor/device IDs, capability bit definitions, vendor log page IDs, feature IDs, customer IDs, telemetry type values, C2 log structures, firmware activation history structures, and utility function prototypes.

## Device and Vendor IDs

The header defines Sandisk and WDC vendor IDs and a large set of device IDs across enterprise and client product families, including SN630, SN640, SN650, SN655, SN861, SN862, SNESSD generations, SN7150, SNCSSD, SN520/SN530/SN350/SN570/SN850X/SN5000/SN7000S, SN7100, SN8000S, SN720/SN730/SN740, ZN350, SN810, SN820CL, and SN5100S variants. `sandisk-utils.c` uses these IDs to map devices to capability flags.

## Capability Flags

The file defines a 64-bit capability flag namespace shared with the WDC plugin. Flags cover:

- internal log and UDUI/DUI capture modes
- C0/C1/C3/CA/D0 and OCP C1/C4/C5 log pages
- drive status, clear assert, clear PCIe, resize, namespace resize
- NAND stats, SMART log support, temperature stats, PCIe stats
- firmware activation history and clear firmware history
- controller telemetry option, reason ID, log page directory, drive info
- cloud SSD/plugin/boot version, cloud log, hardware revision log
- device WAF and latency monitor feature support

Mask macros group related capability variants such as SMART log support, clear PCIe support, internal log support, firmware history support, clear firmware history support, and resize support.

## Log Pages, Features, and Customer Values

Vendor log page IDs include:

- `0xC0` SMART/cloud attributes and EOL status
- `0xC1` error recovery
- `0xC2` firmware activation history or device manageability
- `0xC3` latency monitor
- `0xC4` device capabilities
- `0xC5` unsupported requests
- `0xCA` device info
- `0xCB` firmware activation history
- `0xD0` VU SMART

Feature IDs include `0xC1` for clear firmware activation history and `0xD2` for disabling controller telemetry option. Customer IDs and C2 entry IDs are defined for capability derivation.

## Structures

The header defines:

- `SNDK_UtilsTimeInfo` for local timestamp components.
- `sndk_c2_log_page_header` and `sndk_c2_log_subpage_header` for device manageability log parsing.
- `sndk_c2_cbs_data` for variable-length string entries.
- `sndk_fw_act_history_log_entry_c2` for a single C2 firmware activation history entry.
- `sndk_fw_act_history_log_format_c2` for the full C2 firmware activation history log, including 20 entries and a trailing GUID.

The firmware history structs are packed to match device binary log layout.

## Public API

The prototypes expose PCI/vendor ID lookup, device validation, commit action formatting, C2 log entry parsing, C2 log retrieval/validation, capability detection, serial-name formatting, time/snprint utilities, and telemetry option validation. These functions are consumed primarily by `sandisk-nvme.c`.

## Notable Risks

This header mixes many domains: device IDs, command capability flags, binary log schemas, and utility prototypes. That is pragmatic for a plugin but creates broad rebuild coupling. It includes many standard library and system headers directly, so any translation unit including it inherits a large include surface.
