# sources/test-tools/syzkaller/prog/kfuzztest.go

Purpose: serializes syzkaller argument trees into the KFuzzTest kernel module's flat region/relocation/payload input format.

Important APIs/types/functions: constants for magic/version/alignment/max input; `kFuzzTestWritePrefix`, `isPowerOfTwo`, `roundUpPowerOfTwo`, `padWithAlignment`; generic `sliceQueue`; `kFuzzTestRelocation`, `kFuzzTestRegion`; region/relocation table writers; `kFuzzTestExpandRegion`; and public `MarshallKFuzztestArg`.

Control flow and state: `kFuzzTestExpandRegion` breadth-first expands one logical region, aligns each arg, writes placeholder pointers and relocation records, appends group children, null-terminates string buffers, writes constants by size, and rejects unsupported arg kinds. `MarshallKFuzztestArg` walks reachable regions once, computes region offsets/sizes and relocations, pads each payload region with poison redzones, computes metadata padding for maximum alignment, then writes prefix, region array, relocation table, and payload.

Dependencies and integration: used by `encodingexec.go` for `KFuzzTest` syscalls. Depends on arg concrete types, type alignment, little-endian binary layout, and kernel header format documented in comments.

Risks: unsupported union args and unusual constant sizes panic. Region IDs are derived from visited map order during BFS, so ordering changes affect ABI/tests. `uint32` offsets/sizes assume encoded inputs stay below KFuzzTest max size. String null-termination mutates a local slice, not the original arg.

Test signals: `kfuzztest_test.go` checks power-of-two rounding and exact prefix/region-array/relocation-table/payload bytes for pointer-heavy and flat struct examples.
