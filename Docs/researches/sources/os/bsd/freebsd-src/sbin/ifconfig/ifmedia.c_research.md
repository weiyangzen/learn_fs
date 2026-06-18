# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifmedia.c

`ifmedia.c` implements generic media selection and reporting for interfaces. It registers `media`, `mode`, `mediaopt`, `-mediaopt`, `inst`, and `instance`, plus an `af_media` status callback.

`media_status()` fetches `struct ifmediareq` through libifconfig, prints current and active media, link status, optional down reason, and supported media when `supmedia` is enabled. Status text and media decoding are delegated to libifconfig helpers.

Setters fetch media state once with `ifmedia_getstate()`, mutate `ifm_current`, and register `setifmediacallback()` so `SIOCSIFMEDIA` is issued later. This supports combining media subtype, mode, instance, and options on one command line.

Parsing helpers map subtype/mode/options strings through `ifconfig_media_lookup_subtype()`, `ifconfig_media_lookup_mode()`, and `ifconfig_media_lookup_options()`. Options are comma split with allocated arrays.

Printing helpers produce user-facing media strings and ifconfig-replayable supported media lines. They include top-level type, subtype, non-autoselect mode, option list, and nonzero instance.

Notable behavior: `setifmediacallback()` uses a static `did_it`, so the deferred media ioctl is only performed once per process invocation. `get_media_mode()` returns `INVALID_IFMEDIA` for unknown modes while subtype/options treat unknown names as fatal.
