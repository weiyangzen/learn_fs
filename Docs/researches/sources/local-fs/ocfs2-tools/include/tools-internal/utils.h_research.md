# File Research: sources/local-fs/ocfs2-tools/include/tools-internal/utils.h

## Purpose

Declares internal string trimming utilities for ocfs2-tools.

## Main Contents

- `tools_strchomp()` removes trailing whitespace in-place.
- `tools_strchug()` removes leading whitespace in-place by shifting content.
- `tools_strstrip(str)` macro composes both operations.

## Dependencies and Integration

- Shared by command-line tools and parsers that normalize input/config strings.

## Research Notes

- Functions do not allocate or reallocate; callers must pass mutable strings.
