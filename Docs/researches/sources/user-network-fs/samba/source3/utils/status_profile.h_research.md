# sources/user-network-fs/samba/source3/utils/status_profile.h

## Purpose

`sources/user-network-fs/samba/source3/utils/status_profile.h` declares the profile reporting interface used by `smbstatus`. The source was read as a complete 30-line file.

## Important APIs, Types, and Functions

It declares `status_profile_dump(bool be_verbose, struct traverse_state *state)` and `status_profile_rates(bool be_verbose)`.

## Control Flow

The header has no runtime flow. `status.c` calls these functions when `--profile` or `--profile-rates` is selected.

## State and Persistence Behavior

The dump function receives the shared `traverse_state` so it can emit either text or JSON profile output. Rate mode has no caller-supplied state beyond verbosity.

## Dependencies and Integration Points

It includes `replace.h` and `status.h`, tying the profile API to the `smbstatus` output mode state. Implementations are selected between `status_profile.c` and `status_profile_dummy.c`.

## Risks and Edge Cases

Any signature change requires coordinated updates in the real implementation, dummy implementation, and `status.c`. JSON behavior depends on `struct traverse_state` remaining the shared output contract.

## Test Signals

Compile tests for both profile-enabled and profile-disabled builds plus `smbstatus -P`/`-R` smoke tests cover this header.
