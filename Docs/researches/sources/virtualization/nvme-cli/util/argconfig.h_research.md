# File Research: sources/virtualization/nvme-cli/util/argconfig.h

Public macro and type interface for nvme-cli argument parsing.

Key elements:
- Defines `enum argconfig_types`.
- Provides `OPT_*` macros for flags, suffix numbers, uint/int/long/double/byte/short/increment/string/fmt/file/list/string options, groups, and terminator.
- Provides JSON-conditional `OPT_FLAG_JSON`.
- Provides `VAL_*` macros for option value alias tables.
- Defines `union argconfig_val`, `struct argconfig_opt_val`, and `struct argconfig_commandline_options`.
- Declares parser, help, comma-separated array parser, word-wrap, and seen-check APIs.

Role:
- Used widely by command implementations to declare CLI options compactly.
