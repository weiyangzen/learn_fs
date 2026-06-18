# sources/security-integrity/selinux/libsemanage/src/parse_utils.c

Purpose: shared line-oriented parsing utilities for libsemanage text database backends.

Important APIs/functions: `parse_init`, `parse_release`, `parse_open`, `parse_close`, `parse_dispose_line`, `parse_skip_space`, `parse_assert_noeof`, `parse_assert_space`, `parse_assert_ch`, `parse_assert_str`, `parse_optional_ch`, `parse_optional_str`, `parse_fetch_int`, and `parse_fetch_string`.

Control flow: `parse_skip_space` advances within the current line, disposes exhausted lines, reads new lines with `getline`, strips newline, skips leading whitespace/comments/blanks, and stores both working and original copies. Assertions report filename/line/original text. Fetch helpers extract non-empty strings or decimal integers up to delimiters/whitespace.

State/persistence: `parse_info_t` owns the current line buffers and input stream pointer. `parse_open` treats missing files as success with no stream, enabling absent optional local stores. It uses `fopen(..., "re")` and `__fsetlocking(..., FSETLOCKING_BYCALLER)`.

Risks: parser is not thread-safe per `FILE` without external locking; `parse_optional_str` assumes `info->ptr` is non-NULL; negative integers are rejected by initial digit check. Tests should cover comments, blank files, EOF, missing files, delimiters, trailing whitespace, malformed ints, and diagnostic line numbers.
