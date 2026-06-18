<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/persontab.h -->
# sources/security-integrity/audit-userspace/auparse/persontab.h

## Purpose
Maps Linux process personality values to symbolic names.

## Important APIs, types, and functions
The `_S` table covers `PER_LINUX`, SVR/SCOSVR/OSR/WYSE/XENIX variants, Linux32 variants, IRIX, RISCOS, Solaris, UW7, OSF4, and HPUX personalities.

## Control flow
Generated `person_i2s` is called by `interpret.c:print_personality`, which masks with `PER_MASK` and appends `~ADDR_NO_RANDOMIZE` when set.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Depends on Linux personality constants and local fallback for `ADDR_NO_RANDOMIZE`. Used for `personality` syscall argument decoding.

## Risks and test signals
Risks are personality flag combinations outside the base mask and header drift. Tests should cover base personality, address-randomization flag, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/persontab.h -->
