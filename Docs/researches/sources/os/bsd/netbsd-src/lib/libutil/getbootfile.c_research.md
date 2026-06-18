# File Research: sources/os/bsd/netbsd-src/lib/libutil/getbootfile.c

## Purpose
Returns the booted kernel path.

## Key Details
- Defaults to `_PATH_UNIX`.
- If `CPU_BOOTED_KERNEL` is available, queries `CTL_MACHDEP/CPU_BOOTED_KERNEL`.
- Prepends `/` to the sysctl-provided relative path.
- Uses `secure_path` to reject unsafe non-default kernel paths.

## Dependencies and Role
- Small system metadata helper.
- Security-sensitive because it validates the returned boot kernel path before exposing it.
