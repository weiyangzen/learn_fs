# File Research: sources/os/plan9/9front/sys/src/cmd/aux/icanhasmsi.c

Role: PCI capability scanner that lists devices with MSI capability.

Behavior:
- Reads `/dev/pci` directory entries and opens files ending in `raw`.
- Checks vendor/device word at offset 0 for `0xFFFF`, then checks status register bit 4 for a capabilities list.
- Walks the PCI capability list starting at offset `0x34` by reading next-pointer and capability ID.
- If capability ID `0x05` (MSI) is found, prints the PCI device path without the `raw` suffix.

Failure handling:
- Per-device open/read errors are printed to stderr, but scanning continues.
