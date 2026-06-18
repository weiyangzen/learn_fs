# File Research: sources/virtualization/nbdkit/filters/ddrescue/Makefile.am

Purpose: builds the ddrescue mapfile filter and optional manual page.

Key details:
- Builds `nbdkit-ddrescue-filter.la` from `ddrescue.c`.
- Includes common headers, replacements, and utils.
- CFLAGS include `GNUTLS_CFLAGS`; LIBADD includes `GNUTLS_LIBS`, common utils, replacements, and Windows import support.
- Applies shared linker symbol script when enabled.
- Generates `nbdkit-ddrescue-filter.1` from POD.

Integration notes:
- The filter itself parses text mapfiles and does not directly use TLS in visible code; GNUTLS linkage may be inherited from broader build conventions.
