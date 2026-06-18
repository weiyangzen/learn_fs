# File Research: sources/os/bsd/dragonflybsd/sys/sys/firmware.h

`firmware.h` defines the loadable firmware registration API. `struct firmware` contains a system-wide name, data pointer, byte size, and version.

The API exposes `firmware_register()`, `firmware_unregister()`, `firmware_get()`, and `firmware_put()`, with `FIRMWARE_UNLOAD` allowing unload if unreferenced.

The comments explain the module embedding model: firmware images are registered by unique name, consumers hold references, and multi-image modules treat the first image as master so module unloading is gated by dependent references.
