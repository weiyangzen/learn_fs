# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/parse.c

## Purpose
Common parser helpers for dhclient configuration and lease files.

## Main Elements
- `skip_to_semi()`: recovers from parse errors by consuming to semicolon, newline, or matching brace.
- `parse_semi()`: requires statement terminator.
- `parse_string()`: parses quoted string plus semicolon into allocated memory.
- `parse_ip_addr()`: parses dotted IPv4 into `struct iaddr`.
- `parse_hardware_param()`: parses hardware type and colon-separated hardware address.
- `parse_lease_time()`: parses numeric lease time into host-order `time_t`.
- `parse_numeric_aggregate()`: parses separator-delimited numeric byte/word/dword lists, either into caller buffer or allocated output.
- `convert_num()`: converts string numbers in base 8/10/16 to network-order 8/16/32-bit storage with range warnings.
- `parse_date()`: parses lease date syntax and returns UTC timestamp via `timegm`.

## Dependencies And Integration
Relies on lexer functions `next_token()`/`peek_token()`, tokens from `dhctoken.h`, conversion helpers from `convert.c`, and `cons()` from `tree.c`. Used by client config and lease parsing.

## Risk Notes
`convert_num()` uses shifts based on requested size and is intended only for 8/16/32-bit sizes. Error recovery is permissive to keep parsing after bad statements.
