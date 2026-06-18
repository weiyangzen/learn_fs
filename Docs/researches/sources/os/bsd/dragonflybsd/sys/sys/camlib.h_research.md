# File Research: sources/os/bsd/dragonflybsd/sys/sys/camlib.h

Userland CAM library interface for opening CAM devices, issuing CCBs, and encoding/decoding SCSI command buffers.

Key responsibilities:
- Defines `struct cam_device`, carrying user-supplied path/name/unit data, resolved SIM/bus/target/LUN identity, inquiry data, serial number, negotiated bus settings, and device fd.
- Defines the hard-coded transport device path `XPT_DEVICE` as `/dev/xpt0`.
- Declares open helpers by path, pass device, bus-target-lun tuple, or specific device name/unit.
- Declares CCB lifecycle and submission helpers: `cam_getccb`, `cam_freeccb`, `cam_send_ccb`.
- Declares SCSI buffer/CCB format build, encode, decode, and visitor-based argument hooks.

Dependencies:
- Includes CAM core headers `bus/cam/cam.h` and `bus/cam/cam_ccb.h`.
- Uses `MAXPATHLEN`, CAM ID widths, `struct scsi_inquiry_data`, and `__printflike`.

Notable risks:
- This is ABI-facing userland storage tooling surface; struct layout and function signatures must stay compatible with CAM consumers.
- Format-string based SCSI encoding/decoding relies on the undocumented format grammar implemented elsewhere.
