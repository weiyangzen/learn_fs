# sources/security-integrity/fscrypt/pam/pam.c

## Purpose
`pam.c` provides the C side of the Go/PAM bridge: conversation callback plumbing, data cleanup functions, locked secret copying, secure secret freeing, and message emission.

## Important APIs, Types, and Functions
`conversation` implements `pam_conv`. `goConv` exposes it to Go. Cleanup helpers are `freeData`, `freeArray`, and `freeSecret`. `copyIntoSecret` creates a locked C copy of a secret. `infoMessage` wraps `pam_info`.

## Control Flow
The conversation allocates a response array, iterates PAM messages, dispatches echo-off prompts to Go `passphraseInput`, echo-on prompts to Go `userInput`, prints informational/error messages, and frees partial responses on callback failure. Secret cleanup zeroes via a volatile `memset` function pointer, calls `munlock`, then frees.

## State and Persistence
PAM response arrays and secret copies are heap allocations. `copyIntoSecret` attempts to `mlock` the copied secret but does not report lock failure. No persistent state is written.

## Dependencies and Integration Points
Includes PAM headers, cgo export header, libc allocation/string functions, and `sys/mman.h`. Called from `pam.go` for transactions and handle data management.

## Risks
`mlock`/`munlock` return values are ignored in the C helpers. Conversation messages that do not match known styles are not explicitly handled beyond the switch fallthrough behavior. Correct cleanup depends on PAM invoking registered cleanup functions.

## Test Signals
No direct C unit tests. PAM wrapper and module tests are mostly stubs, so this bridge is primarily validated by build/link success and external integration.
