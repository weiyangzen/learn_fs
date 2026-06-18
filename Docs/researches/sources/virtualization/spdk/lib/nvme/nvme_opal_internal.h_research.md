# File Research: sources/virtualization/spdk/lib/nvme/nvme_opal_internal.h

## Purpose

Internal definitions for `nvme_opal.c`. It centralizes Opal buffer sizing, UID/method tables, parsed response token types, session state, and the private `spdk_opal_dev` representation.

## Main Contents

- Constants: `IO_BUFFER_LENGTH` 2048, `MAX_TOKS` 64, `OPAL_KEY_MAX` 256, `OPAL_UID_LENGTH` 8, host session number, invalid-parameter value, and missing-method-status value.
- Atom/token enums: internal token classes for byte strings, signed/unsigned integers, raw Opal tokens, and atom widths.
- UID enum and `spdk_opal_uid` table for SMUID, Admin SP, Locking SP, Anybody, SID, Admin/User authorities, locking ranges, ACEs, C_PIN objects, PSID, and half UIDs.
- Method enum and `spdk_opal_method` table for Properties, StartSession, Revert, Activate, GenKey, Get, Set, Authenticate, Random, Erase, and related methods.
- Internal structs for keys, parsed response tokens, response token arrays, Opal packet header grouping, session state, and device state.

## Integration Points

Included directly by `nvme_opal.c`; also includes `spdk/opal_spec.h`, `spdk/opal.h`, and `spdk/scsi_spec.h`. The UID and method arrays are definitions in the header, so this header is intended for narrow internal inclusion rather than broad reuse.

## Risk Notes

Because the UID/method arrays are non-static definitions in a header, including this header in multiple translation units would create duplicate definitions. Current use appears intentionally local to `nvme_opal.c`.
