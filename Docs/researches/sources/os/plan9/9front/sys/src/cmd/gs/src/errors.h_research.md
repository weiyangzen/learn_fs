# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/errors.h

## Scope

Backward-compatibility header for Ghostscript client API error codes.

## Key Behavior

- Documents that client API error codes were moved to `ierrors.h`.
- Includes `ierrors.h` under the old `errors.h` name.

## Dependencies

Depends only on `ierrors.h`.

## Risks And Invariants

- Kept to avoid breaking older clients that include `errors.h`.
- New code should include `ierrors.h` directly to avoid namespace ambiguity.
