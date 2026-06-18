# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/side-trace.c

Parses side trace telemetry objects.

Main behavior:
- Side trace is parsed in 256-byte blocks.
- Each entry starts with a configured `trimmedSideTraceBufferEntryHeader`.
- Empty token `0xffff` is skipped.
- Unknown token labels terminate parsing.
- Emits parsed entries under `fwSideTrace`.

Entry handling:
- Reads `majorRev`, `minorRev`, `tokenId`, and `payloadSize` from dynamically parsed header output.
- Major revision `>= 128` is treated as a trimmed entry.
- Older entries use `sideTraceBufferEntry` version 6.0.
- Trimmed entries may include raw payload byte array under `payload.rawDataArray`.

Metadata:
- Adds `parseType`, `fileSizeBytes`, `blockSize`, and `totalEntriesParsed` to object metadata.

Risks/notes:
- Uses config-driven parsing heavily; missing header definitions result in no decoded entries.
- `ctx.output` is stored in context but not directly used by `parse_side_trace_entry()`.
