# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/conflex.c

## Purpose
Lexical scanner for dhclient configuration and lease parsers.

## Main Elements
- Tracks source name, line/column, current/previous line buffers, and a one-token peek buffer.
- `new_parse()`: resets lexer state for a file.
- `get_char()`: reads characters while maintaining line buffers and positions.
- `get_token()`, `next_token()`, `peek_token()`: tokenize whitespace/comments, strings, numbers, identifiers, and punctuation.
- `read_string()`: handles quoted strings with backslash escaping.
- `read_number()` and `read_num_or_name()`: read numeric and identifier-like tokens.
- `intern()`: maps known dhclient/dhcp keywords to token constants, otherwise returns the default token class.

## Dependencies And Integration
Included by `clparse.c` and other dhclient parsers through `dhcpd.h` and `dhctoken.h`.

## Risk Notes
Token text uses a fixed 1500-byte buffer with warnings and truncation if exceeded. Identifier interning is extensive and case-insensitive.
