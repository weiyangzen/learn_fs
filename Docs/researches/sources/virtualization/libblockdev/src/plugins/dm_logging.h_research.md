# File Research: sources/virtualization/libblockdev/src/plugins/dm_logging.h

## Role

`dm_logging.h` declares the libdevmapper log redirection callback used by the dm plugin.

## Public Surface

It declares `redirect_dm_log()` with GLib's printf-format checking attribute over arguments 5 and 6.

## Dependencies

Only GLib is included.

## Notable Risks

The header is internal-style support for `dm.c`, not a stable user-facing dm operation API.
