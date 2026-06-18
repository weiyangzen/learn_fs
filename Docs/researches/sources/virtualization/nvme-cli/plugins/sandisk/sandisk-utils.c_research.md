# File Research: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-utils.c

## Role

`sandisk-utils.c` implements the shared utility layer behind the Sandisk plugin. It handles device/vendor identification, device support checks, commit-action formatting, C2 device manageability log retrieval and parsing, capability-bitmask construction, serial-based filename generation, local time capture, snprintf wrapping, and controller-initiated telemetry option validation.

## UUIDs and Device Identity

The file defines three UUID constants:

- `WDC_UUID`
- `WDC_UUID_SN640_3`
- `SNDK_UUID`

These are used to retrieve vendor C2 device manageability log pages with the correct UUID index. `sndk_get_pci_ids()` locates the controller or namespace in libnvme topology, reads vendor/device IDs from sysfs, and parses them with `strtol()`. If sysfs probing fails in higher-level checks, `sndk_get_vendor_id()` falls back to `nvme_identify_ctrl()` and reads the controller vendor ID.

`sndk_check_device()` accepts Sandisk and WDC vendor IDs and rejects other vendors with an error message.

## C2 Device Manageability Parsing

The C2 log parsing helpers operate on a log whose top-level header is `sndk_c2_log_page_header`, followed by repeated `sndk_c2_log_subpage_header` entries:

- `sndk_parse_dev_mng_log_entry()` walks entries until it finds the requested entry ID, validating entry sizes, remaining length, and entry ID range.
- `sndk_nvme_parse_dev_status_log_entry()` extracts a `__u32` entry value.
- `sndk_nvme_parse_dev_status_log_str()` extracts variable-length string data from a CBS-style entry body.
- `sndk_validate_dev_mng_log()` validates the overall log entry sequence.
- `sndk_get_dev_mgmt_log_page_data()` reads log page `0xC2` using the selected UUID index, reallocates if the real length exceeds the initial 4 KiB buffer, validates the log, and returns a right-sized copy to the caller.
- `sndk_get_dev_mgment_data()` chooses Sandisk UUID first, then WDC UUID, then the SN640/SN655 UUID, defaulting to UUID index 0 if UUID lists are unsupported.

The parser intentionally treats malformed lengths, zero entry size, out-of-range entry IDs, and unaligned ends as invalid.

## Capability Detection

`sndk_get_drive_capabilities()` first obtains PCI IDs, falling back to identify vendor ID for NVMe-oF style devices where device ID may be unavailable. With a known vendor/device pair, it maps supported device IDs to capability flags. SN861, SN862, SNESSD, SN7150, SNCSSD, SNTMP, and WDC device families receive different combinations of internal log, C0/C3/CA/OCP log pages, UDUI, firmware history, clear feature, drive status, resize, cloud version, log-page directory, and latency monitor capabilities.

If the device ID is unavailable but a vendor ID is present, it delegates to `sndk_get_enc_drive_capabilities()`. If no Sandisk capability mapping matches, it falls back to `run_wdc_get_drive_capabilities()`.

`sndk_get_enc_drive_capabilities()` is the capability path for identified vendor but unknown/enclosure-style devices. For WDC vendor IDs it starts with a base capability set, selects a C2 UUID index, verifies C2 support via WDC helpers, reads C2 manageability data, extracts customer ID, marketing name, and form factor, checks individual supported log pages, and adds OCP/SN861-specific capabilities based on customer IDs or marketing name/form factor.

## Miscellaneous Utilities

`sndk_get_commit_action_bin()` maps commit action values 0 through 7 to binary-looking strings `000b` through `111b`, otherwise `INVALID`.

`sndk_get_serial_name()` identifies the controller, trims trailing spaces from the serial number, and formats a filename using an existing prefix plus serial plus suffix.

`sndk_UtilsGetTime()` fills `SNDK_UtilsTimeInfo` from local time and timezone offset.

`sndk_UtilsSnprintf()` is a thin `vsnprintf()` wrapper.

`sndk_check_ctrl_telemetry_option_disabled()` reads vendor feature ID `0xD2`; a nonzero result means controller-initiated telemetry is disabled and the helper returns `-EINVAL`.

## Dependencies and Integration

The file includes libnvme, nvme-cli command helpers, `sandisk-utils.h`, and WDC command helpers. It is the main dependency of `sandisk-nvme.c` for device validation and capability routing.

## Notable Risks

`sndk_get_dev_mgmt_log_page_data()` allocates data for callers but the ownership contract is implicit; callers must free it. `sndk_get_enc_drive_capabilities()` obtains `dev_mng_log` but does not free it before returning, which appears to leak that buffer. Several functions rely on sysfs paths and libnvme topology state being available. `sndk_nvme_parse_dev_status_log_str()` copies a length from device data into the caller buffer without taking the caller buffer capacity.
