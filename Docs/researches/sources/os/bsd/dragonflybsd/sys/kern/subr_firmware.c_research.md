# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_firmware.c

## Summary
Implements the loadable firmware registry and autoload/unload machinery for firmware images backed by kernel modules.

## Main Responsibilities
- Maintains a fixed `FIRMWARE_MAX` table of `priv_fw` records.
- `firmware_register()` and `firmware_unregister()` add/remove named firmware images and parent/child module relationships.
- `firmware_get()` looks up firmware, autoloading a module by image name when permitted.
- `firmware_put()` drops references and may request deferred unload.
- `loadimage()` and `unloadentry()` run module reference/release work on a dedicated firmware taskqueue.
- Module glue creates the taskqueue and validates clean unload.

## Important Behavior
`fw.name` marks a registered image; `file` marks an autoloaded module whose unload handling is still pending. Parent firmware records receive refcount bumps from child images. Autoload is blocked by `SYSCAP_NOKLD` privilege failure or positive `securelevel`.

## Risks
The registry is a fixed 30-slot static array because external users hold firmware pointers. `firmware_unregister()` preserves `file` for autoloaded entries, so cleanup depends on later unload task state. Module unload fails if any image remains registered.
