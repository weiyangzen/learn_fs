# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/prompt.c

## Purpose
`prompt.c` gets and sets the interactive prompt for an ss invocation.

## Important APIs, Types, and Functions
Public functions are `ss_set_prompt()` and `ss_get_prompt()`.

## Control Flow
`ss_set_prompt()` frees the existing prompt and stores the caller-provided new prompt pointer. `ss_get_prompt()` returns the current pointer from `ss_data`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is `ss_data.prompt`. Dependencies are `ss_internal.h`. Risks include ownership transfer being implicit, potential free of non-malloc strings if caller misuses the API, and no NULL validation. Test signals are changed prompts in interactive sessions and correct prompt returned by getter.
