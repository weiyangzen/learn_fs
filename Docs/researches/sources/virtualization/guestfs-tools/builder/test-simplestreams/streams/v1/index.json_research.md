# File Research: sources/virtualization/guestfs-tools/builder/test-simplestreams/streams/v1/index.json

## Scope

Simplestreams index fixture for virt-builder tests.

## Contents

- Declares `format: index:1.0`.
- Points to one product stream, `net.cirros-cloud:released:download`.
- Lists product IDs for CirrOS standard 0.3 on i386, x86_64, powerpc, and arm.
- References product metadata path `streams/v1/net.cirros-cloud_released_download.json`.

## Risks And Invariants

- Tests expect this fixture to resolve into the supported templates listed by `test-virt-builder-list-simplestreams.sh`.
- The arm product lacks disk image data in the companion fixture, so list output intentionally covers only usable disk images.
