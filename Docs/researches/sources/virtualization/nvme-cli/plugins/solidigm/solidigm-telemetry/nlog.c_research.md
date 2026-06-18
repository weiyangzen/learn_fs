# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/nlog.c

Parses NLOG circular buffers into JSON events.

Main behavior:
- Treats the buffer as an array of 32-bit words.
- Searches possible starting offsets up to max log entry size.
- Chooses the offset with the fewest header sequence mismatches.
- Builds output key `"events"` as an array of event arrays.

Event format:
- Timestamp/value word.
- Second timestamp/value word.
- Header.
- Parameter array.
- Format object from config.

Config dependency:
- `formats_find()` looks up format strings by 32-bit header formatted as `0x%08X`.

Risks/notes:
- Assumes `buff_size` is divisible by 4 for word parsing.
- Emits warning when more than one header mismatch is detected in the best offset.
