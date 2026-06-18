# File Research: sources/virtualization/nvme-cli/unit/test-argconfig-parse.c

C unit test for `util/argconfig.c`.

Coverage:
- Tests parsing of flags, suffixed integers, uint/int/long/double/byte/short/increment/string/fmt/file/list/str options.
- Tests option value aliases with prefix matching and ambiguity/error cases.
- Tests comma-separated `u32` array parsing, including empty input, invalid tokens, overflow, sparse commas, and max-length overflow.
- Tests global option parsing before subcommands, including verbose increments, dry-run flag, stopping at first non-option, option without subcommand, and unknown option failure.
- Captures stderr for selected global parse tests via `tmpfile`, `dup`, and `dup2`.

Role:
- Guards command-line parser behavior, especially global parser semantics needed by subcommand dispatch.
