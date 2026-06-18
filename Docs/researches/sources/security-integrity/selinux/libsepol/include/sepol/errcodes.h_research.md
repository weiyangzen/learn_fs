# sources/security-integrity/selinux/libsepol/include/sepol/errcodes.h

Purpose: Defines shared libsepol status and error-code constants.

Important APIs and symbols: `SEPOL_OK`, legacy `SEPOL_ERR`, `SEPOL_ENOTSUP`, `SEPOL_EREQ`, and errno-mapped `SEPOL_ENOMEM`, `SEPOL_EEXIST`, `SEPOL_ENOENT`.

Control flow: No logic exists. Functions throughout libsepol return these values for success, allocation failure, duplicate entries, missing entries, and unsupported requests.

State and persistence: No state.

Dependencies and integration points: Includes `<errno.h>` and is used by policydb, hashtab, avtab, CIL tests, and public APIs.

Risks: Negative errno mapping is part of API behavior. Mixing these constants with internal `STATUS_ERR` conventions requires careful translation at public boundaries.

Test signals: Unit tests should assert exact return values for duplicate/missing/allocation-style paths where API documentation promises them.
