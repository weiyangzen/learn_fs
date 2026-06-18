# File Research: sources/virtualization/nbdkit/filters/extentlist/Makefile.am

Automake rules for building `nbdkit-extentlist-filter.la`. The filter sources are `extentlist.c` plus the public filter header.

Includes top-level common rules and header paths for `include`, generated include, common include, replacements, and utils. Links against common utils, compatibility replacements, and the Windows import library hook.

Optionally applies the shared filter linker version script and builds the `nbdkit-extentlist-filter.1` man page from POD when POD tooling is available.
