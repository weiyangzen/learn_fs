# File Research: sources/virtualization/guestfs-tools/inspector/inspector.c

## Role

C implementation of `virt-inspector`, the tool that inspects disk images or libvirt guests and emits structured XML describing detected operating systems, filesystems, mountpoints, drive mappings, installed applications, and optional icons.

## Major Responsibilities

The program creates a global libguestfs handle, parses common guestfs options, adds drives, launches the appliance, decrypts inspected devices when keys are provided, runs `guestfs_inspect_os`, and writes XML to stdout.

Supported command-line behavior includes `-a`, `-d`, `--connect`, `--format`, `--blocksize`, LUKS key options, `--no-applications`, `--no-icon`, tracing/verbose/version/help, and a modal `--xpath` mode. Old-style syntax is preserved by treating path-like arguments as image files and other arguments as domain names.

## XML Output

The output path uses libxml2 writer macros. For each root, it canonicalizes the root device, emits OS type, architecture, distro, product name/variant, major/minor version, package format/manager, Windows systemroot/current control set/group policy where available, hostname, optional build ID, osinfo ID, mountpoints, filesystems, drive mappings, applications, and optional base64 icon data.

Mountpoints are sorted by path length then name. Filesystems are sorted by device name. Drive mappings are sorted case-insensitively. Application output includes all populated `guestfs_application2` fields.

## XPath Mode

`--xpath` reads XML from stdin, evaluates the supplied XPath expression, and prints node-set, string, or scalar results. This mode forbids disk/domain options and exits after processing.

## Research Notes

The file is mostly glue over libguestfs inspection APIs, but it is the canonical definition of the XML schema shape consumed by the expected `*.img.xml` fixtures.
