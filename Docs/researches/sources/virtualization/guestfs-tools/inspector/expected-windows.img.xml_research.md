# File Research: sources/virtualization/guestfs-tools/inspector/expected-windows.img.xml

## Role

Golden XML output for `virt-inspector` against the phony Windows guest image.

## Contents

The document describes one Windows guest rooted at `/dev/sda2`. It reports `name` and `distro` as `windows`, architecture `i386`, product `Microsoft Windows 7 Phony Edition`, product variant `Client`, version `6.1`, systemroot `/Windows`, current control set `ControlSet001`, hostname `windows.invalid`, and osinfo ID `win7`.

It records a single `/` mountpoint and NTFS filesystem on `/dev/sda2` with UUID `091A29CC586B609C`. It also includes one drive mapping, `C` to `/dev/sda2`.

The applications section has four Windows application entries. These exercise registry-derived fields including display name, version, URL, install path, publisher, description, and WOW6432Node-style 32-bit application detection.

## Research Notes

This fixture validates the Windows-specific branches in inspector output: registry-derived identity, current control set, drive mappings, NTFS metadata, and application metadata.
