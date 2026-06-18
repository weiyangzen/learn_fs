# File Research: sources/virtualization/guestfs-tools/test-data/phony-guests/guests.xml.in

Autoconf-substituted libvirt test driver XML for phony guests.

Key behavior:
- Documents use with `test://@abs_builddir@/guests.xml`.
- Defines domains for:
  - no disks,
  - deliberately missing disk,
  - blank disk variants,
  - Debian,
  - Fedora variants,
  - Ubuntu,
  - Arch Linux,
  - CoreOS,
  - Windows.
- Each disk-backed domain points at `@abs_builddir@/<image>.img` as raw virtio disk.
- Windows domain also defines a network interface and qxl video device.
- Comments document LUKS passwords for Fedora encrypted variants.

Research notes:
- Provides negative and positive libvirt test cases, including missing disk handling and non-guest blank images.
