<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/prepare.inc.sh -->
# sources/security-integrity/keyutils/tests/prepare.inc.sh

## Purpose
Shared preparation script for the keyutils test tree. It ensures each test runs inside a private session keyring, optionally under a watched session, initializes environment/version variables, and derives feature flags.

## Important APIs, Types, And Functions
Defines `has_kernel_config`, session bootstrap logic around `keyctl watch_session` and `keyctl session`, RHTS integration, `OSDIST`, `OSRELEASE`, `KEYUTILSVER`, `KERNELVER`, `TEST`, and feature booleans such as `have_key_invalidate`, `have_big_key_type`, `have_dh_compute`, `have_restrict_keyring`, and `have_notify`.

## Control Flow
When not called with `--inside-test-session`, it re-execs the current test under a named session keyring. If notification support is present, it also creates watch and GC logs and exposes a watch fd to the child. Inside the session it initializes RHTS or local `$OUTPUTFILE`, detects distro and keyutils version, sources `version.inc.sh`, derives the test name from the working directory, probes feature support, and reads skip flags from the environment.

## State And Persistence Behavior
The script replaces the process with a child running in a new session keyring. It writes `watch.out`, `gc.out`, and `test.out`/RHTS output. Feature flags are shell variables consumed by runtest scripts and `toolbox.inc.sh`.

## Dependencies And Integration Points
Requires `keyctl`, `lsb_release`, optionally `rpm`, RHTS environment scripts, and kernel config files. It integrates with `version.inc.sh`, `toolbox.inc.sh`, and all keyctl test scripts via sourced shell state.

## Risks And Edge Cases
Re-exec argument handling is delicate because `$0` and `$@` are reused. Distro/version detection assumes `lsb_release` and keyutils version output formats. Notification setup changes fd state and creates side logs.

## Test Signals
Signals are successful re-exec into a private session, correct feature variables, and consistent `$TEST` naming for report output.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/prepare.inc.sh -->
