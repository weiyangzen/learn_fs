# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/parse.y

## Purpose
`parse.y` implements the yacc grammar and lexer for `dhcpleased.conf`.

## Main Responsibilities
- Parses interface blocks and per-interface DHCP client options.
- Supports macros with `name = value` and `$name` expansion.
- Supports quoted strings with escapes and line continuations.
- Tracks file stack state, line numbers, unget buffers, EOF handling, and parse errors.
- Validates optional “secret” file permissions through `check_file_secrecy()`, though the main config path is pushed as non-secret.
- Builds `struct dhcpleased_conf` with `iface_conf` entries.
- Frees nonpersistent macros after parsing and warns about unused macros at high verbosity.

## Grammar Features
Supported interface options include:
- `send vendor class id STRING`
- `send client id STRING`
- `send host name STRING`
- `send no host name`
- `ignore routes`
- `ignore dns`
- `ignore STRING` for server IPv4 addresses
- `prefer ipv6`

Client ID strings are first parsed as colon-separated hex bytes including the type byte; if that fails, they are parsed as escaped text. Vendor class IDs and text client IDs are decoded with `strnunvis()` and serialized into DHCP option buffers.

## Important APIs
- `parse_config(const char *filename)`: returns a parsed config, an empty config for missing default config, or `NULL` on parse/open errors.
- `cmdline_symset(char *s)`: stores a persistent macro from `name=value`.
- `conf_get_iface(char *name)`: finds or creates an interface config.

## Integration Notes
The parser builds the same config structures later sent by the main process to frontend and engine. `printconf.c` can print the parsed config back out.

## Risk Notes
Duplicate options for the same interface are parse errors. Interface names longer than `IF_NAMESIZE` terminate via `errx`. The lexer has its own macro-expansion sentinels to avoid recursive expansion state confusion.
