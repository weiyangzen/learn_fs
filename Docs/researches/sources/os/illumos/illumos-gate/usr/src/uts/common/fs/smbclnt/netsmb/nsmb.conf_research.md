# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb.conf

## Purpose

`nsmb.conf` is the driver configuration file for the illumos SMB client kernel module.

## Contents

After the CDDL header and copyright block, it declares:

```text
name="nsmb" parent="pseudo";
```

This attaches the `nsmb` device as a pseudo device rather than a hardware-enumerated device.

## Dependencies

The file is consumed by illumos driver/module configuration tooling and corresponds to the `nsmb` SMB client pseudo-device.

## Research Notes

There is no executable logic here. The main operational effect is module attachment under the `pseudo` parent.
