# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/csiioctl.h

Small ioctl-number header for codeset-independent communication between `stty(1)` and the `ldterm(4M)` line discipline.

Key elements:
- Defines the `CSI_IOC` command prefix.
- `CSDATA_SET` asks `ldterm` to accept an `ldterm_cs_data_t` definition and switch locale/codeset methods when valid.
- `CSDATA_GET` asks `ldterm` to return the currently active codeset data.

Dependencies:
- The comments reference `ldterm_cs_data_t`, defined elsewhere in the terminal/line-discipline headers.
- Used by terminal control paths that configure multibyte or locale-specific character-width behavior.

Research notes:
- This header only defines ioctl command values and explanatory comments; payload validation and codeset switching are implemented in `ldterm`.
