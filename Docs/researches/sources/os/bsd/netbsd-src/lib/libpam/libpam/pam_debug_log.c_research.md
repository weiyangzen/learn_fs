# File Research: sources/os/bsd/netbsd-src/lib/libpam/libpam/pam_debug_log.c

Local PAM helper for verbose module errors. `_pam_verbose_error` suppresses output when `PAM_SILENT` or `no_warn` is set, derives the module name from the source filename, formats the message with `vasprintf`, and reports it through `pam_error`.

It is exposed to modules through `pam_mod_misc.h` and wrapped by `PAM_VERBOSE_ERROR`.
