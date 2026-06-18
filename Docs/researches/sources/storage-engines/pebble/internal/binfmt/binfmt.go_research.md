# sources/storage-engines/pebble/internal/binfmt/binfmt.go

Purpose: Provides a binary formatter that consumes a byte slice and emits annotated, aligned descriptions of binary layouts.

APIs and types: `New`, `Formatter`, methods for prefixes, anchor offsets, relative data, widths, offsets, peeking integers, binary/hex/uvarint formatting, treeprinter output, unsafe pointers, and `Line` builder methods.

Control flow and state: `Formatter` tracks `off`, `anchorOff`, original data, line width, and buffered `(binary, comment)` lines. Formatting calls consume bytes and append aligned output. `Line` enforces that the caller formats exactly the declared number of bytes.

Persistence and dependencies: Runtime diagnostic formatter only. Depends on binary encoding, bytes buffers, math/strconv/string formatting, treeprinter, and unsafe pointer access.

Integration points: Used by tools/tests that explain table, blob, or WAL binary structures.

Risks: Most methods assume enough remaining bytes and will panic on out-of-range or assertion failures. `Pointer` exposes unsafe pointers into the backing slice. `HexBytesln` returns the depleted local `n` (zero after consumption), so callers should not expect original length.

Test signals: No direct test for `Formatter` in this subset; `hexdump_test.go` covers the simpler hexdump utility.
