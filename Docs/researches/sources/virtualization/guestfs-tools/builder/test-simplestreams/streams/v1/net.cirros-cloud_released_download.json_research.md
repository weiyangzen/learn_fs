# File Research: sources/virtualization/guestfs-tools/builder/test-simplestreams/streams/v1/net.cirros-cloud_released_download.json

## Scope

Simplestreams product metadata fixture for CirrOS image-download tests.

## Contents

- Declares products under `net.cirros-cloud:standard:0.3` for i386, x86_64, powerpc, and arm.
- Provides versioned items with `ftype`, `md5`, `sha256`, `size`, and `path`.
- i386 and x86_64 include multiple dated versions from CirrOS 0.3.0 through 0.3.4 with `disk.img`, `lxc.tar.gz`, and `uec.tar.gz`.
- powerpc includes 0.3.4 disk image metadata.
- arm contains LXC/UEC items but no `disk.img`, which makes it unsuitable as a virt-builder disk template.
- Includes top-level `datatype: image-downloads`, `format: products:1.0`, update timestamp, and content ID.

## Test Role

- Drives Simplestreams parsing and filtering.
- Expected list output selects latest usable disk images for powerpc, x86_64, and i386.

## Risks And Invariants

- Exact sizes, names, and architecture ordering are asserted by tests.
- Changes to Simplestreams selection logic can alter which product versions appear.
