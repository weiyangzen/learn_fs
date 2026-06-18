# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/609

## Purpose
This fixture covers a normal `WARNING` report titled `WARNING: zero-size vmalloc in dvb_dmx_init`. It represents a USB DVB probe path that requests a zero-sized vmalloc region.

## Important APIs, types, and functions
Important frames include `__vmalloc_node_range`, `vmalloc`, `dvb_dmx_init`, `dvb_usb_adapter_dvb_init`, `dvb_usb_device_init`, `cxusb_probe`, `usb_probe_interface`, `really_probe`, `device_add`, and `hub_event`.

## Control flow
The kernel worker `kworker/0:1` handles `usb_hub_wq hub_event`, probes a USB device, enters DVB initialization, and triggers the warning in vmalloc validation.

## State and persistence behavior
The fixture stores a complete warning stack but no mutable state. The parser-relevant persistent state is the expected `TITLE` and `TYPE` at the top.

## Dependencies and integration points
It links syzkaller report parsing with Linux USB, driver core, media/DVB, and memory-management warning formats.

## Risks and test signals
The parser must prefer the semantic title `zero-size vmalloc in dvb_dmx_init`, not a generic `WARNING in __vmalloc_node_range`. The `TYPE: WARNING` header is the oracle.
