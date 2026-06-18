# File Research: sources/virtualization/nvme-cli/plugins/netapp/netapp-nvme.c

## Role

Implements the NetApp nvme-cli plugin commands:

- `smdevices`: list NetApp E-Series volumes.
- `ontapdevices`: list NetApp ONTAP NVMe namespaces.

The implementation scans `/dev` for NVMe namespace block devices, opens each with libnvme, identifies NetApp devices by controller model string, collects namespace/controller metadata, and prints normal, column, or JSON output.

## Device Types

Two internal structures model collected data:

- `struct smdevice_info`: E-Series namespace data with NSID, controller identify data, namespace identify data, and device path.
- `struct ontapdevice_info`: ONTAP namespace data with NSID, controller identify data, namespace identify data, namespace UUID, ONTAP C2 log data, and device path.

## Constants and ONTAP Log Format

Important constants:

- `ONTAP_C2_LOG_ID`: `0xC2`.
- `ONTAP_C2_LOG_SIZE`: `4096`.
- Label/path lengths: `ONTAP_LABEL_LEN`, `ONTAP_NS_PATHLEN`.

ONTAP C2 log LSPs:

- `0x0`: supported.
- `0x1`: namespace info.
- `0x2`: platform.

ONTAP namespace info TLVs:

- `0x11`: vserver name.
- `0x12`: volume name.
- `0x13`: namespace name.
- `0x14`: namespace path.

`nvme_get_ontap_c2_log()` builds a Get Log Page admin passthrough for log `0xC2`, namespace info LSP, and target NSID.

## Device Discovery

`netapp_nvme_filter()` is used by `scandir("/dev", ...)`. It accepts names matching `nvme%d n%d` namespace devices and rejects hidden files and partition names matching `nvme%dn%dp%d`.

Both command handlers optionally accept a target device name after options and validate it with `/dev/<name>` plus an `nvmeXnY` pattern.

## E-Series Flow

`netapp_smdevices()`:

1. Creates libnvme global context.
2. Parses options.
3. Validates output format.
4. Scans `/dev`.
5. Opens each NVMe namespace device.
6. Calls `netapp_smdevices_get_info()`.
7. Prints matching devices.

`netapp_smdevices_get_info()`:

- Identifies controller.
- Requires model name prefix `NetApp E-Series`.
- Gets NSID via `libnvme_get_nsid()`.
- Identifies namespace.
- Stores device path.

E-Series output derives:

- Array name from controller vendor-specific bytes at `ctrl.vs[20]`, converted from UCS-2-ish layout by `netapp_convert_string()`.
- Volume name from namespace vendor-specific bytes.
- Volume ID from namespace NGUID.
- Controller side from `ctrl.vs[0] & 0x1`.
- Namespace size, block size, and firmware version from identify data.

## ONTAP Flow

`netapp_ontapdevices()` mirrors `smdevices` but calls `netapp_ontapdevices_get_info()`.

`netapp_ontapdevices_get_info()`:

- Identifies controller.
- Requires model name prefix `NetApp ONTAP Controller`.
- Gets NSID and namespace identify data.
- Allocates namespace descriptor list and reads it with `nvme_identify_ns_descs_list()`.
- Copies UUID from the namespace descriptor payload.
- Reads ONTAP C2 namespace info log.

ONTAP output derives:

- Vserver and namespace path from C2 TLVs via `netapp_get_ontap_labels()`.
- Subsystem name from the suffix of `ctrl.subnqn`.
- UUID from namespace descriptor data.
- Size, used bytes, block size, and firmware version from identify data.

## Output Modes

`netapp_output_format()` supports:

- `normal`
- `column`
- `json` when `CONFIG_JSONC` is available

E-Series output helpers:

- `netapp_smdevices_print_regular()`
- `netapp_smdevices_print_verbose()`
- `netapp_smdevices_print_json()`
- `netapp_smdevice_json()`

ONTAP output helpers:

- `netapp_ontapdevices_print_regular()`
- `netapp_ontapdevices_print_verbose()`
- `netapp_ontapdevices_print_json()`
- `netapp_ontapdevice_json()`

Verbose mode adds used size, block format, and firmware version.

## Utility Functions

- `netapp_convert_string()` squashes UCS-2-like label strings into ASCII by taking every second byte.
- `netapp_nguid_to_str()` formats a 16-byte NGUID as 32 lowercase hex chars.
- `netapp_get_ns_size()` computes human-readable namespace size using SI suffixes.
- `netapp_get_ns_attrs()` computes size, used bytes, block size, and firmware version.
- `ontap_get_subsysname()` strips trailing spaces from target NQN and extracts the final dot-separated component.
- `ontap_labels_to_str()` copies printable ONTAP label bytes.
- `netapp_get_ontap_labels()` walks expected TLV order and composes namespace path from volume/name if explicit path TLV is absent.

## Dependencies

Uses:

- libnvme open/close, identify controller, identify namespace, namespace descriptors, NSID lookup, admin passthrough.
- nvme-cli JSON helpers, global output format, verbose flag.
- `util/suffix.h` for SI/binary suffix formatting.
- Linux `/dev` namespace naming assumptions.

## Notes

- Device classification is based on model string prefixes, not vendor ID.
- The ONTAP namespace UUID extraction assumes descriptor layout by copying after one `struct nvme_ns_id_desc`.
- Several helper functions use fixed-size buffers and `sprintf()`/`snprintf()` with known internal data sizes.
- Access state is printed as `unknown` for both E-Series modes.
