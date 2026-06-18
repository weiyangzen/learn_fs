# sources/user-network-fs/samba/source3/lib/util_specialsids.h

## Purpose
This header declares the Asserted Identity SID helper interface used by source3 SID/name mapping code.

## Important APIs and Types
It forward-declares `struct dom_sid` and declares `sid_check_is_asserted_identity`, `sid_check_is_in_asserted_identity`, and `asserted_identity_domain_name`.

## Dependencies and Integration Points
The header includes `replace.h` for base portability types and leaves the full SID definition to callers. It is paired directly with `util_specialsids.c`.

## Risks and Test Signals
Because it only declares functions, compatibility risk is ABI/API drift if signatures change. Compile tests should verify inclusion from modules that only have a forward declaration available and from modules that include the full security headers.
