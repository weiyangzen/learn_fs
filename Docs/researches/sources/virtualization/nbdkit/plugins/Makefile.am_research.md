# File Research: sources/virtualization/nbdkit/plugins/Makefile.am

This top-level plugin Automake file includes common rules, distributes `plugins.syms`, and delegates plugin builds to `SUBDIRS = $(plugins)`. The actual plugin list is provided by the configured `$(plugins)` variable elsewhere in the build system.

Its role is structural: it ties all enabled plugin subdirectories into the recursive build while keeping common plugin symbol export metadata in `EXTRA_DIST`.

There is no direct compilation logic here; platform and dependency gating happens in each plugin subdirectory's `Makefile.am`.
