# File Research: sources/local-fs/ocfs2-tools/libo2dlm/capabilities.c

## Purpose

Reads ocfs2_dlmfs module capabilities and exposes capability checks to libo2dlm callers.

## Main Contents

- Reads `/sys/module/ocfs2_dlmfs/parameters/capabilities`.
- Trims the trailing newline from the capabilities line.
- `o2dlm_has_capability()` searches for a named capability token, requiring end-of-string or space after the match.
- Public checks:
  - `o2dlm_supports_bast()` for blocking AST support.
  - `o2dlm_supports_stackglue()` for stack glue support.
- Optional `DEBUG_EXE` main prints capability status for `bast`, `stackglue`, and an invalid capability.

## Dependencies and Integration

- Includes `o2dlm/o2dlm.h` for error codes and public declarations.
- Used by tooling that needs to adapt to available dlmfs features.

## Research Notes

- Missing capabilities file is treated as an empty capability set; other read errors become service unavailable.
- Matching is substring-based with a right-boundary check but no explicit left-boundary check, so capability names should be unique enough to avoid suffix collisions.
