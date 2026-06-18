## sources/storage-engines/pebble/sstable/block/flush_governor_test.go

Purpose: Datadriven black-box tests for `FlushGovernor` construction and flush decisions.

Important APIs/types/functions: `TestFlushGovernor` calls `block.MakeFlushGovernor`, `FlushGovernor.String`, and `ShouldFlush`. It can use custom size classes or `sstable.JemallocSizeClasses`.

Control flow: The `init` command reads target block size, block-size threshold, size-class-aware threshold, and classes, then prints watermarks. The `should-flush` command evaluates a `sizeBefore`/`sizeAfter` pair and emits whether the governor would flush.

State and persistence behavior: Test state is a single `FlushGovernor` persisted across commands in the datadriven file.

Dependencies and integration points: Uses `datadriven`, external package `block_test`, and `sstable.JemallocSizeClasses`, giving coverage closer to public usage.

Risks: Coverage depends on testdata breadth. It does not fuzz arbitrary class arrays or assert panic/fallback behavior for malformed classes.

Test signals: Good regression coverage for writer-facing watermarks and decisions.
