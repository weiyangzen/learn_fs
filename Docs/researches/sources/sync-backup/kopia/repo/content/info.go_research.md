# sources/sync-backup/kopia/repo/content/info.go

## Purpose
Provides content-package aliases and small conversion helpers over `repo/content/index` identifiers and metadata. This keeps callers using `content.ID`, `content.Info`, and `content.IDRange` without importing the lower-level index package directly.

## Important APIs, Types, And Functions
Aliases include `ID`, `IDPrefix`, `Info`, and `IDRange`; `EmptyID` re-exports `index.EmptyID`. Functions are `IDFromHash`, `ParseID`, `IDsFromStrings`, and `IDsToStrings`.

## Control Flow
`IDFromHash` and `ParseID` delegate to index validation/parsing. `IDsFromStrings` loops through string inputs, parsing each and wrapping parse errors with the offending string. `IDsToStrings` maps each ID through `String()`.

## State And Persistence
This file has no mutable state and no persistence. It defines stable API surface for content identifiers.

## Dependencies And Integration Points
It depends on `repo/content/index` and `pkg/errors`. It is used by content APIs, verification, deletion, and callers that need identifier parsing without reaching into index internals.

## Risks And Edge Cases
The main edge case is invalid user-supplied content ID strings; `IDsFromStrings` stops on the first invalid value. Since these are aliases, behavioral compatibility follows the index package exactly.

## Test Signals
No dedicated tests are in this subset. Coverage is expected indirectly through content manager and verification tests that parse or compare content IDs.
