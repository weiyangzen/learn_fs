# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/mode.h

This generic SCSI header defines common MODE SENSE/MODE SELECT headers, block descriptors, mode page headers, mode page constants, and common mode page structures.

Key definitions:
- Defines 6-byte and 10-byte mode parameter headers.
- Defines block descriptors and macros to locate block descriptors and mode pages inside a mode response.
- Defines common `struct mode_page` with endian-dependent page code/saveable bitfields.
- Defines page-control values for current/changeable/default/saved pages.
- Defines common mode page codes, including disconnect/reconnect, format, geometry, caching, peripheral device, control mode, power condition, informational exceptions, and all pages.
- Defines structures for:
  - disconnect/reconnect page
  - generic caching page
  - peripheral device page
  - SCSI-3 control mode page
  - informational exceptions page
  - power condition page
  - log parameter control
  - start/stop cycle counter log
- Includes direct-access device mode definitions and implementation-specific mode variants.

Dependencies:
- Includes `generic/dad_mode.h` and `impl/mode.h`.

Impact:
- This is the common mode-page parsing/building contract for target drivers.
- It bridges standard mode pages and illumos implementation-specific legacy forms.

Cautions:
- Pointer arithmetic macros assume well-formed buffer layout and caller-provided type correctness.
- Several structures use endian-dependent bitfields.
