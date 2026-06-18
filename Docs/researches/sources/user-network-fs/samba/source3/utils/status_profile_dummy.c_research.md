# sources/user-network-fs/samba/source3/utils/status_profile_dummy.c

## Purpose

`sources/user-network-fs/samba/source3/utils/status_profile_dummy.c` provides profile API fallbacks when Samba is built without profiling support. The source was read as a complete 35-line file.

## Important APIs, Types, and Functions

It defines `status_profile_dump` and `status_profile_rates`, matching `status_profile.h`.

## Control Flow

Both functions print `Profile data unavailable` to stderr and return `true`. This lets `smbstatus -P` or `-R` link and finish without profile support, though no profile data is shown.

## State and Persistence Behavior

No state is read or written. Arguments are ignored apart from signature compatibility.

## Dependencies and Integration Points

The file includes `smbprofile.h` and `status_profile.h` for ABI compatibility. `wscript_build` selects it when `WITH_PROFILE` is not configured.

## Risks and Edge Cases

Returning success after printing an unavailable message can make automation think a profile command succeeded. If stricter semantics are desired, the caller or dummy implementation would need to return failure.

## Test Signals

Profile-disabled builds should link `smbstatus`, and `smbstatus -P`/`-R` should print the unavailable message without crashing.
