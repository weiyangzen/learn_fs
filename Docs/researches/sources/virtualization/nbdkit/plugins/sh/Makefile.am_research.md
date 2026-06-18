# File Research: sources/virtualization/nbdkit/plugins/sh/Makefile.am

Automake rules for the shell plugin, disabled on Windows because it depends on shell scripting. It builds `nbdkit-sh-plugin.la` from the process runner, method dispatcher, shell front-end, subplugin abstraction, tempdir support, and public plugin header.

The build uses nbdkit/common include paths, common utilities, Windows import hook placeholders, module/shared libtool flags, and optional plugin linker script. It distributes POD documentation and example scripts, and conditionally generates `nbdkit-sh-plugin.3`.
