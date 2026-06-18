# sources/test-tools/xfstests/tests/generic/374

## Purpose
Check that cross-mountpoint dedupe works. It is registered as generic/374 with `_begin_fstest` tags `auto, quick, clone, dedupe`, making it part of the reflink/shared extents, dedupe coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, filter_md5. Important state variables and paths include testdir=$SCRATCH_MNT/test-$seq, otherdir=$tmp.m.$seq, othertestdir=$otherdir/test-$seq, blocks=1, blksz=65536, sz=$((blocks * blksz)). Topic focus: reflink/shared extents, dedupe. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; deduplicates matching byte ranges; writes deterministic byte patterns; requires dedupe support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, filter_md5.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_scratch_dedupe.

External/helper commands: $MOUNT_PROG, md5sum, mkdir, mount, rm, sed.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Mount otherdir; Create file; Dedupe one file to another; deduped 65536/65536 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec). Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
