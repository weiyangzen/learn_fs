# File Research: sources/virtualization/nbdkit/plugins/random/Makefile.am

Automake rules for building `nbdkit-random-plugin.la` from `random.c`. It wires in nbdkit public headers, common include/utils paths, warnings, compatibility replacements, Windows import-library support, module/shared libtool flags, and the optional plugin linker version script.

Also distributes the POD manual source and conditionally generates `nbdkit-random-plugin.1`, inserting the shared magic-parameter documentation when POD tooling is available.
