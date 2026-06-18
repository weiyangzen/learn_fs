# File Research: sources/teaching/minix/minix/drivers/storage/ramdisk/rc

## Purpose

Boot-time shell script run from the MINIX ramdisk to start early services, locate the root device, check/mount the root filesystem, and hand off to `/etc/rc`.

## Main Steps

On i386, it starts ACPI when configured, PCI, input/keyboard, procfs, and one primary storage stack: AHCI, virtio block, or AT disk, with floppy started non-critically. It probes virtio by checking `/proc/pci` unless the environment overrides it. On ARM, it starts the MMC driver.

It then starts ramdisk-local procfs, determines `rootdevname` from environment, CD probing, `/dev/ram`, or embedded image ramdisk mode, optionally loads a RAM disk image, runs `fsck_mfs` unless CD boot is active, mounts the root filesystem, reopens standard descriptors away from the ramdisk, mounts procfs on the real root, and executes NetBSD rc infrastructure.

## Dependencies

Depends on `sysenv`, `minix-service`, `mount`, `umount`, `grep`, `cdprobe`, `loadramdisk`, `fsck_mfs`, and service binaries placed in the ramdisk image by the Makefile.

## Risks

Root selection is environment-sensitive. The script tolerates some early service failures but exits if required root selection fails or CD probing cannot find media. Storage-driver selection order matters: AHCI overrides virtio, which overrides AT disk unless environment variables change behavior.
