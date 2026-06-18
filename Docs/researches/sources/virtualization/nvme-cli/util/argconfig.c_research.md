# File Research: sources/virtualization/nvme-cli/util/argconfig.c

Command-line parsing utility implementation for nvme-cli.

Key elements:
- Maintains appended usage string for help output.
- Prints word-wrapped descriptions and option help.
- Builds `getopt_long_only` option tables dynamically from `argconfig_commandline_options`.
- Parses typed values: string, int, byte, short, uint/positive, increment, long, binary-suffix long, double, and flag.
- Supports enum-like option value tables with case-insensitive prefix matching; ambiguous prefixes fail.
- Tracks whether each option was seen.
- Resets locale to `C` unless a `human-readable` flag option was seen.
- Provides `argconfig_parse_global`, using a leading `+` in the short option string so parsing stops at the first non-option subcommand.
- Generates comma-separated array parsers for int, short, long, and fixed-width unsigned integer types.
- Provides `argconfig_parse_seen`.

Dependencies:
- Uses `getopt`, `suffix_binary_parse`, cleanup attributes, and `libnvme_strerror`.

Notes:
- Global parser uses `getopt_long` while subcommand parser uses `getopt_long_only`.
- Comma-separated array parsing mutates the input string through `strtok`.
