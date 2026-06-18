# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/getexpiration.c

Provides expiration-date prompting for account tools. `getdate` parses `YYYYMMDD` into a `Tm`; `getexpiration` reads the current expiration from `<db>/<user>/expire`, displays it as a default, then prompts for `YYYYMMDD` or `never`.

It validates that new expiration is in the future and within two years. Return values are epoch seconds, `0` for never, or `-1` when the user accepts no change.
