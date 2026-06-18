# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vscan.h

## Role

`vscan.h` defines the kernel/user interface for the illumos virus-scan service module and its `vscand` daemon.

## Key Interfaces

The header defines the device path prefix `/dev/vscan/vscan` and ioctl commands for:
- enabling the door rendezvous,
- disabling during daemon shutdown,
- updating configuration,
- returning scan results,
- setting maximum in-progress requests.

Scan statuses include undefined, no scan required, error, clean, infected, and scanning.

`vs_scan_req_t` is sent to the daemon and includes request index, sequence number, file size, flags, modified/quarantined indicators, path, and scanstamp.

`vs_scan_rsp_t` is the async daemon response with index, sequence number, result, and updated scanstamp.

`vs_config_t` carries file-type filters, maximum file size, and allow/deny behavior for oversized files.

## Kernel Hooks

Kernel declarations cover vscan service lifecycle, configuration, in-use check, result/abort handling, vnode lookup by request, door lifecycle/open/close, scanning a file via door, and driver node creation.

## Research Notes

This header depends on `AV_SCANSTAMP_SZ` from `vnode.h`. It is a coordination ABI between filesystem access paths, the vscan kernel service, and the external daemon.
