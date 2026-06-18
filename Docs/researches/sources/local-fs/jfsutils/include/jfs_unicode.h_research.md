# File Research: sources/local-fs/jfsutils/include/jfs_unicode.h

Inline Unicode string and uppercase helpers for JFS 16-bit `UniChar` names.

Key contents:
- Declares `UniUpperTable` and `UniUpperRange` generated uppercase conversion tables.
- Defines `struct UNICASERANGE`.
- Provides inline helpers:
  - `UniStrcpy`
  - `UniStrlen`
  - `UniStrncmp`
  - `UniStrncpy`
  - `UniToupper`
  - `UniStrupr`
- `UniToupper()` uses a 512-entry base table for low characters and range tables for higher characters.

Interactions:
- Used for JFS directory/name handling, especially case handling for OS/2-style semantics.

Research notes:
- Header assumes `UniChar` and `size_t` are already visible from prior includes.
