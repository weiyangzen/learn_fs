# sources/user-network-fs/samba/source3/profile/profile_dummy.c

## Purpose

`profile_dummy.c` provides stub implementations when profiling is unavailable in the build. It keeps callers linkable without creating profiling state.

## Important APIs, Types, and Functions

- `profile_setup()` always returns true.
- `set_profile_level()` logs that profiling support is unavailable.

## Control Flow

There is no setup logic. Calls to configure profiling do not change runtime state and only emit a notice.

## State and Persistence

No state is allocated or persisted.

## Dependencies and Integration Points

It includes `smbprofile.h` to match the real profiling API. Build selection chooses this file instead of `profile.c` for non-profiling builds.

## Risks and Edge Cases

Callers that assume profiling commands have an effect will receive success from setup but no data will be produced. That is the intended compatibility behavior for builds without profiling support.

## Test Signals

Compile/link tests should verify the stub satisfies required symbols. Runtime tests should confirm profile setup succeeds and profile-level changes do not crash.
