# File Research: sources/virtualization/nbdkit/filters/map/Makefile.am

This Automake fragment builds `nbdkit-map-filter.la` from `map.c` and the public filter header, distributes `nbdkit-map-filter.pod`, and generates `nbdkit-map-filter.1` plus HTML through `podwrapper.pl` when POD support is enabled. It includes common nbdkit build rules and wires include paths for core headers, `common/regions`, and `common/utils`.

The filter links against `libregions.la`, `libutils.la`, compatibility replacements, and the Windows import library when applicable. It uses module-style libtool flags with optional linker-version script support via `filters/filters.syms`.

Integration risk is mostly build-contract drift: `map.c` depends on the regions and utility helpers named here, so changes to range mapping helpers or Windows no-undefined behavior must keep these library and include dependencies in sync.
