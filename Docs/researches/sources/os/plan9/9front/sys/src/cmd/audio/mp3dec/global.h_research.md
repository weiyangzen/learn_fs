# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/global.h

This is the small global portability/configuration header for the 9front libmad copy. It includes Plan 9 system headers `<u.h>` and `<libc.h>`, replacing the broader autoconf/platform headers used by upstream libmad in many builds.

It also enforces that `OPT_SPEED` and `OPT_ACCURACY` are mutually exclusive, and implicitly enables `OPT_SSO` when `OPT_SPEED` is selected. Those flags affect arithmetic and synthesis optimization choices in fixed-point code and other libmad modules.

This file is included by most implementation files before local decoder headers. Its role is not algorithmic; it establishes the Plan 9 compilation environment and shared compile-time feature rules. Because it uses Plan 9 headers directly, this source tree is adapted for 9front rather than a generic portable libmad checkout.
