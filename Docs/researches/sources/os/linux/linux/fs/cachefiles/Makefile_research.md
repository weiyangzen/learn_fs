# File Research: sources/os/linux/linux/fs/cachefiles/Makefile

## Purpose
Builds the CacheFiles module object list.

## Main Elements
- Core objects: `cache.o`, `daemon.o`, `interface.o`, `io.o`, `key.o`, `main.o`, `namei.o`, `security.o`, `volume.o`, and `xattr.o`.
- Optional objects: `error_inject.o` under `CONFIG_CACHEFILES_ERROR_INJECTION` and `ondemand.o` under `CONFIG_CACHEFILES_ONDEMAND`.
- Module target: `obj-$(CONFIG_CACHEFILES) := cachefiles.o`.

## Dependencies And Integration
Mirrors the Kconfig features and links CacheFiles into the kernel build as one composite module.

## Risk Notes
Feature-gated source files must stay aligned with prototypes and stubs in `internal.h`, especially on-demand and error-injection paths.
