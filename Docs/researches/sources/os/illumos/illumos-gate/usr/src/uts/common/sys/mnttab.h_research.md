# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mnttab.h

Purpose: Defines mount table record structures and userland parsing/query functions.

Key definitions:
- `MNTTAB`, `MNT_LINE_MAX`, and parse errors for too long/too many/too few fields.
- `mntnull()` macro and disabled `putmntent()` macro.
- `struct mnttab`: special, mount point, fstype, options, time.
- `struct extmnttab`: same initial layout plus major/minor.
- `struct mntentbuf`: extended entry pointer and backing buffer.

Key APIs outside kernel:
- `resetmnttab()`
- `getmntent()`
- `getextmntent()`
- `getmntany()`
- `hasmntopt()`
- `mntopt()`

Important detail: Comments require matching field layout across `mnttab`, `extmnttab`, `mntentbuf`, and their 32-bit kernel counterparts so code can safely cast between related record types.

Relevance to subset A: Direct mount table user/kernel ABI.
