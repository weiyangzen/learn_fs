# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/Makefile

## Purpose

This Makefile controls installation and header checking for the common illumos `sys` include tree. It is a manifest for exported kernel/user headers and many structured subdirectories.

## Main Content

The file includes `$(SRC)/uts/Makefile.uts`, sets installed header mode to `644`, and documents several private headers present in the kernel but not shipped. It defines machine-specific headers, generated headers (`priv_const.h`, `priv_names.h`, `usb/usbdevs.h`), and a large `CHKHDRS` list of common public/private checked headers.

It then defines subdirectory header groups for audio, AV, crypto, DCAM, i2c, InfiniBand/RDMA, Fibre Channel, filesystem internals, GPIO, NVMe, SCSI, SATA, USB, 1394, hotplug, RSM, Trusted Solaris, network drivers, and platform headers.

## Build Targets

`CHECKHDRS` maps each group to `.check` targets using `DOT_H_CHECK`. `.PARALLEL` enables parallel checking/installing. `install_h` installs root header targets after directory creation. `all_h` builds generated headers. The generated headers are produced with AWK scripts, and `clean`, `clobber`, and `check` provide maintenance targets.

## Research Notes

For research indexing, this file identifies which headers are considered part of the illumos header surface. It is metadata-heavy but important for understanding exported ABI/API boundaries.
