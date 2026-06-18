# File Research: sources/virtualization/guestfs-tools/inspector/expected-ubuntu.img.xml

## Role

Golden XML output for `virt-inspector` against the phony Ubuntu guest image.

## Contents

The document describes one Linux `x86_64` Ubuntu guest rooted at `/dev/sda2`. It reports product `Ubuntu 10.10 (Phony Pharaoh)`, version `10.10`, package format `deb`, package management `apt`, hostname `ubuntu.invalid`, and osinfo ID `ubuntu10.10`.

It records mountpoints for `/` on `/dev/sda2` and `/boot` on `/dev/sda1`. The filesystems section includes `/dev/mapper/cryptswap1` with no type/label/UUID metadata, `/dev/sda1` as ext2 with label `BOOT`, and `/dev/sda2` as ext2 with a deterministic UUID.

The applications section contains three Debian-style test packages, each with `source_package`, URL, summary, and multiline description.

## Research Notes

This fixture verifies Debian package metadata handling, swap-like block devices with sparse filesystem metadata, and Ubuntu-specific inspector fields.
