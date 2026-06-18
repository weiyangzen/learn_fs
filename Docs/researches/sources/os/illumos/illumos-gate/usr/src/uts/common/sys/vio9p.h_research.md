# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vio9p.h

## Role

`vio9p.h` defines the small public ioctl contract for illumos virtio 9P channel devices.

## Key Interfaces

The header defines:
- `VIRTIO_9P_TAGLEN` as 32 bytes, the maximum mount-tag length when the hypervisor advertises the mount-tag feature.
- `VIO9P_IOC_BASE`, using the characters `9` and `P` in the ioctl namespace.
- `VIO9P_IOC_MOUNT_TAG`, the ioctl for retrieving the mount tag.
- `VIO9P_MOUNT_TAG_SIZE`, one byte larger than the maximum tag to allow NUL termination.

## Research Notes

This file is intentionally narrow: it does not define 9P protocol structures, only the illumos device ioctl needed by consumers to discover virtio 9P channel metadata.
