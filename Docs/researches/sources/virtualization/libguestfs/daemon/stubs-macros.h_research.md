# File Research: sources/virtualization/libguestfs/daemon/stubs-macros.h

## Role
Defines daemon stub helper macros used by generated action stubs to normalize device, mountable, and path-or-device arguments before dispatching to implementation functions.

## Main Responsibilities
- `RESOLVE_DEVICE` runs `device_name_translation`, validates the result with `is_device_parameter`, and cancels pending FileIn transfers on argument failure.
- `RESOLVE_MOUNTABLE` parses `btrfsvol:` descriptors into `mountable_t`, otherwise resolves ordinary device strings.
- `REQUIRE_ROOT_OR_RESOLVE_DEVICE` accepts either a valid device parameter or an absolute path inside the mounted guest root.
- `REQUIRE_ROOT_OR_RESOLVE_MOUNTABLE` accepts either a device/mountable descriptor or an absolute path represented as `MOUNTABLE_PATH`.

## Error Handling
The macros reply through daemon protocol helpers and return directly from the caller. File upload paths call `cancel_receive()` before reporting validation failures.

## Filesystem/Storage Relevance
This header is part of the trust boundary for daemon filesystem APIs. It decides whether strings are treated as guest filesystem paths, appliance device names, or btrfs subvolume mountables.
