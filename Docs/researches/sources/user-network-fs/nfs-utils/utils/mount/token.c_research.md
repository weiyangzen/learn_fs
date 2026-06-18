<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/token.c -->
# sources/user-network-fs/nfs-utils/utils/mount/token.c

## Purpose

`token.c` provides a small reentrant tokenizer for mount option parsing. It avoids `strtok`, does not modify the input string, and treats delimiters inside double quotes as literal characters.

## Important APIs, types, and functions

`struct tokenizer_state` stores the current position, delimiter, and error code. `init_tokenizer` allocates state, `next_token` returns a newly allocated token, `tokenizer_error` exposes parse/allocation errors, and `end_tokenizer` frees state. Private helpers skip leading delimiters and find the next delimiter while tracking quote state.

## Control flow

Each `next_token` call skips delimiter runs, stops at string end, scans until an unquoted delimiter, and returns `strndup` of the token. If the input ends inside an open quote, it records `EINVAL`; if allocation fails, it records `ENOMEM`. On no-token or error, it nulls `pos` and returns `NULL`.

## State and persistence behavior

The tokenizer state is heap-allocated and advances monotonically through the caller-provided string. Returned tokens are independent heap strings owned by the caller. The module performs no I/O or persistence.

## Dependencies and integration points

It is used by `parse_opt.c` to split comma-delimited mount options such as SELinux contexts containing quoted commas. The opaque state is declared in `token.h`.

## Risks and edge cases

Quotes are toggled by every double quote; there is no escape handling. Empty tokens from repeated delimiters are skipped. A trailing open quote stops tokenization with `EINVAL`, which callers must check after the loop.

## Test signals

Tests should cover repeated delimiters, leading/trailing delimiters, quoted delimiters, unmatched quotes, allocation-failure behavior where practical, and nested independent tokenizers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/token.c -->
