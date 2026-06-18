<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/sucap/Makefile -->
# sources/security-integrity/libcap/contrib/sucap/Makefile

## Purpose
Makefile for `sucap`, a PAM/libcap demonstration of an su-like program using capabilities.

## Important APIs, Types, And Functions
Defines `LINKEXTRA`, `DEPS`, target `su`, and `clean`. Builds `su.c` with `PAM_APP_NAME="sucap"`, links PAM, pam_misc, and libcap, then applies file capabilities with `sudo setcap`.

## Control Flow
Builds in-tree `libcap.so` dependency, compiles the program with an rpath to the in-tree library, and assigns permitted capabilities needed for chown, gid/uid changes, DAC read/search, and setpcap.

## State And Persistence Behavior
Creates `su` and persists file capability xattrs on it. Clean removes build outputs but not necessarily external PAM configuration.

## Dependencies And Integration Points
Depends on PAM development libraries, in-tree libcap, sudo, setcap, and `su.c` outside this work item.

## Risks And Edge Cases
The build invokes sudo and grants powerful file capabilities to a local executable. Runtime behavior also depends on PAM service configuration.

## Test Signals
Signals are successful link and `setcap` application to `./su`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/sucap/Makefile -->
