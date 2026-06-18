# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_util.c

## Purpose
Small shared utility implementation for the illumos `zpool` command sources.

## Main Elements
- `safe_malloc()`: zeroed allocation with process exit on failure.
- `zpool_no_memory()`: ENOMEM assertion, localized error, and exit.
- `num_logs()`: counts immediate child vdevs marked as log devices.
- `array64_max()`: finds the maximum uint64 array element.
- `isnumber()`: permissive digit/dot screening for CLI interval/count parsing.

## Dependencies And Integration
- Includes `zpool_util.h`.
- Uses nvlist APIs and ZFS config keys.
- `safe_malloc()` is used across zpool command code for fail-fast allocation.
- `array64_max()` supports histogram column sizing.
- `isnumber()` supports interval/count parsing in list, status, iostat, and wait flows.

## Risk Notes
- `safe_malloc()` exits instead of returning failure.
- `isnumber()` accepts loose forms like `.` or multiple dots; stricter parsing happens later.
- `num_logs()` is shallow and does not recurse into nested vdevs.
