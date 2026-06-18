# File Research: sources/virtualization/guestfs-tools/test-data/phony-guests/make-guests-all-good.pl

Perl generator for `guests-all-good.xml`.

Key behavior:
- Emits libvirt test-driver XML for each image argument that exists and is non-empty.
- Uses current working directory as output disk path base.
- Converts image filename to domain name by stripping `.img`.
- Each generated domain has one raw virtio disk and standard hvm boot metadata.

Research notes:
- Unlike `guests.xml.in`, this generated XML omits deliberately broken/missing-disk cases.
