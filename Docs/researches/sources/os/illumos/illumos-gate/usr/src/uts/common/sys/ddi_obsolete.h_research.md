# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_obsolete.h

This header collects obsolete DDI interfaces that remain available when `_DDI_STRICT` is not defined. It includes basic types, DDI opaque types, and LDI event types.

It declares legacy `strtol`/`strtoul` and obsolete memory and I/O accessor functions. The `ddi_mem_get*`, `ddi_mem_put*`, `ddi_mem_rep_get*`, and `ddi_mem_rep_put*` families operate through access handles on memory mappings. The `ddi_io_get*`, `ddi_io_put*`, `ddi_io_rep_get*`, and `ddi_io_rep_put*` families provide older I/O-space accessors.

The file also declares obsolete LDI event interfaces: `ldi_get_eventcookie`, `ldi_add_event_handler`, and `ldi_remove_event_handler`.

Research notes:
- The entire functional surface is hidden under `#ifndef _DDI_STRICT`.
- New code should avoid these symbols in favor of current DDI access and LDI event APIs.
- This file exists for compatibility and source migration.
