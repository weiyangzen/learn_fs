# File Research: sources/virtualization/guestfs-tools/inspector/expected-fedora.img.xml

## Role

Golden XML output for `virt-inspector` against the phony Fedora guest image. It validates the complete inspector serialization path for a Fedora-like Linux guest.

## Contents

The document has one `<operatingsystem>` under `<operatingsystems>`. It identifies root `/dev/VG/Root`, Linux `x86_64`, distro `fedora`, product `Fedora release 14 (Phony)`, version `14.0`, RPM/yum packaging, hostname `fedora.invalid`, and osinfo ID `fedora14`.

It records two mountpoints: `/dev/VG/Root` mounted at `/`, and `/dev/sda1` mounted at `/boot`. It records two ext2 filesystems with labels `ROOT` and `BOOT` and deterministic UUIDs.

The large body is an `<applications>` list with 172 RPM application entries. Entries include package metadata fields such as `name`, optional `epoch`, `version`, `release`, `arch`, `url`, `summary`, and multiline `description`. The list exercises stable ordering and rich RPM metadata extraction, including packages from base system utilities through systemd, rpm, glibc, kernel/core boot packages, and ending with `zlib`.

## Research Notes

This file is not executable code; it is a regression oracle. It is especially important because it checks that `virt-inspector` emits package descriptions, summaries, architecture, release, epoch, filesystem labels, UUIDs, and canonicalized device names exactly as expected.
