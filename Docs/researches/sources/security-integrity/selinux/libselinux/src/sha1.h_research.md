<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/sha1.h -->
# sources/security-integrity/selinux/libselinux/src/sha1.h

## Purpose
Declares the small SHA-1 API and data structures used internally by libselinux.

## Important APIs, Types, And Functions
Defines `Sha1Context`, `SHA1_HASH_SIZE`, `SHA1_HASH`, and prototypes for `Sha1Initialise()`, `Sha1Update()`, and `Sha1Finalise()`.

## Control Flow
No executable control flow.

## State And Persistence Behavior
All hash state is caller-owned in `Sha1Context`.

## Dependencies And Integration Points
Included by label digest internals and paired with `sha1.c`.

## Risks And Test Signals
Compile checks and known-answer hash tests validate the declaration/implementation contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/sha1.h -->
