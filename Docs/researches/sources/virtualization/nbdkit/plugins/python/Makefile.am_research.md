# File Research: sources/virtualization/nbdkit/plugins/python/Makefile.am

## Purpose
Builds the embedded Python plugin adapter and distributes example Python plugins.

## Main Contents
When Python support is available, defines `nbdkit-python-plugin.la` from `errors.c`, `helpers.c`, `modfunctions.c`, `plugin.c`, `plugin.h`, and the plugin header. It includes nbdkit/common paths, compiles with Python CFLAGS, links Python libraries and nbdkit utilities, applies plugin module flags and optional linker script, and generates `nbdkit-python-plugin.3`.

## Dependencies
Gated by `HAVE_PYTHON`; documentation generation is gated by `HAVE_POD`.

## Risks and Notes
The adapter build depends on Python embed/link flags matching the target interpreter. The listed examples are installed/distributed as documentation and test material, not linked into the plugin.
