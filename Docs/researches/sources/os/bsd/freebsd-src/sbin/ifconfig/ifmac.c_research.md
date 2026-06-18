# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifmac.c

`ifmac.c` adds MAC Framework label support to ifconfig. It registers `maclabel` and an `af_maclabel` status callback.

`maclabel_status()` prepares an ifnet label with `mac_prepare_ifnet_label()`, fetches it via `SIOCGIFMAC`, converts it with `mac_to_text()`, and prints non-empty labels. `setifmaclabel()` parses a label from text with `mac_from_text()` and applies it through `SIOCSIFMAC`.

Dependencies include `<sys/mac.h>`, standard ifreq ioctls, and `ifconfig.h`. Label memory is released with `mac_free()`, and text output from `mac_to_text()` is freed normally.

Notable behavior: most failures are silent or printed with `perror()` rather than fatal, so unsupported MAC labeling does not break general ifconfig status output.
