# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/zns.c

## Role

`zns.c` tests libnvme ioctl command initializers for Zoned Namespace commands using the same mock ioctl infrastructure as `ioctl/misc.c`.

## Behavior

The test opens the synthetic `NVME_TEST_FD` handle and runs four tests: ZNS append, report zones, management send, and management receive.

`test_zns_append()` validates opcode, NSID, zone SLBA splitting, NLB/control encoding, variable-size tag setup through `nvme_init_var_size_tags()`, application tag setup through `nvme_init_app_tag()`, and copied data.

`test_zns_report_zones()` validates management receive command fields for report options, extended reporting, partial reporting, data length in dwords, and response payload copying.

`test_zns_mgmt_send()` and `test_zns_mgmt_recv()` validate action-specific fields in CDW13 and payload behavior.

## Dependencies

- Includes `<libnvme.h>`.
- Uses `mock.h` and `util.h`.
- Relies on libnvme ZNS command initializer helpers.

## Filesystem/Storage Relevance

This is directly relevant to zoned block-storage behavior: it verifies userspace command construction for ZNS zone append and zone management operations.
