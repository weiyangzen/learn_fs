# sources/sync-backup/bup/lib/bup/cmd/list_idx.py

## Purpose
`list_idx.py` inspects bup/git `.idx` or `.midx` files and prints object hashes, optionally limited by a hex prefix.

## APIs and Control Flow
`main(argv)` validates at least one filename, converts `--find` to bytes, checks length <= 40 and valid hex after padding odd nibble counts, then opens each object index with `git.open_object_idx`. If the prefix is a full 40 hex chars it uses `exists`; otherwise it exhaustively scans hashes and writes matching `filename hash` lines.

## State, Dependencies, Integration, Risks, Tests
It is read-only. Dependencies are `git.open_object_idx`, `hexlify/unhexlify`, `add_error`, `handle_ctrl_c`, and progress output. It is a diagnostic companion to pack/midx maintenance. Risks include slow exhaustive scans for short prefixes, continuing after index-open errors through saved error state, and path byte/string handling. Test signals include invalid hex rejection, odd-length prefix padding, full-hash fast path, exhaustive prefix output, multiple index handling, and Ctrl-C handling.
