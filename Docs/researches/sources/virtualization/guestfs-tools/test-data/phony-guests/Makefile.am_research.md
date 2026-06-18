# File Research: sources/virtualization/guestfs-tools/test-data/phony-guests/Makefile.am

Automake file for generating minimal “phony” guest disk images and libvirt test XML.

Key behavior:
- Distributes image generator scripts, package/registry fixtures, Fedora journal/database fixtures, Windows hive fixtures, and `guests.xml.in`.
- Defines generated disk images: blank variants, Debian, Fedora variants, Ubuntu, Arch Linux, CoreOS, and Windows.
- Uses `check_DATA` so images are built for `make check`.
- Provides rules for blank images through `guestfish -N`.
- Builds Fedora variants through `make-fedora-img.pl` with `LAYOUT` values: `partitions`, `partitions-md`, `btrfs`, `luks-on-lvm`, `lvm-on-luks`.
- Builds Debian/Ubuntu/Arch/CoreOS/Windows through corresponding scripts.
- Generates `guests-all-good.xml` from image list.
- Builds `fedora.db` from compressed SQL using sqlite.
- Builds a static helper binary `fedora-static-bin` from `fedora.c`.
- Generates Windows `SOFTWARE` and `SYSTEM` hives by merging `.reg` files into `minimal-hive`.
- Marks guest image construction `.NOTPARALLEL` to reduce memory pressure.

Research notes:
- This directory provides reusable inspectable test images for many guestfs-tools tests.
