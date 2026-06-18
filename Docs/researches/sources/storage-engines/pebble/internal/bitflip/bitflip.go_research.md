# sources/storage-engines/pebble/internal/bitflip/bitflip.go

Purpose: Provides a diagnostic helper that searches for a single-bit flip that would make a byte slice match an expected checksum.

APIs and types: `CheckSliceForBitFlip` and internal `checkByteForFlip`.

Control flow and state: Scans up to 40 KiB of the slice, flips each bit of each byte, computes checksum, restores the byte, and returns the first index/bit that matches the expected checksum.

Persistence and dependencies: Mutates the provided slice transiently but restores each bit before returning. No external dependencies.

Integration points: Useful in corruption diagnostics to identify likely one-bit memory or disk corruption.

Risks: O(n*8*checksum) and capped at 40 KiB, so it may miss flips beyond the cap or multi-bit corruption. A checksum collision can produce a false positive.

Test signals: No direct test in this subset; behavior is straightforward but relies on checksum callback correctness.
