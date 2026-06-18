# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/common.c

## Purpose
Shared canonicalization and pattern-matching engine for spam/scanning tools.

## Main Interfaces
- `readmsg`: reads full headers plus at least a body prefix for scanning.
- `convert`, `conv64`: canonicalize header/body text, lowercasing, whitespace folding, HTML stripping, MIME escape handling, and base64 body conversion.
- `parsepats`: loads pattern files into regexp and hashed literal structures.
- `matchpat`: matches literal or regexp patterns with alternate exclusions.
- `xprint`: prints match context.

## Behavior
Headers are detected with care for fractured headers and embedded NULs. Body canonicalization removes most HTML tags while preserving URLs/forms/images of interest. Patterns can be actions such as `DUMP`, `HEADER`, `HOLD`, `LINE`, and `LINEOFF`, with string patterns introduced by `*` and alternate exclusions separated by `~~`.

## Dependencies
`regexp.h`, `bio.h`, `spam.h`, global `header` and `cmd` buffers supplied by callers, Plan 9 `dec64`.

## Risks / Notes
- Only bounded canonical buffers are produced (`Hdrsize`, `Bodysize`, `Maxread`).
- The file ends with a static base64 decode table; local conversion uses `dec64`.
- HTML handling is heuristic and intentionally lossy for spam matching.
