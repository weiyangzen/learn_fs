<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/aarch64/memcpy.S -->
# sources/storage-engines/foundationdb/flow/aarch64/memcpy.S
- Purpose: Optimized AArch64 implementation shared by `memcpy` and `memmove`.
- Important APIs/types/functions: Exports `memmove` as an alias and `memcpy` as the main entry, with register aliases for source/destination bounds and SIMD quad registers.
- Control flow: Splits copies into small (0-32 bytes), medium (33-128 bytes), and large paths. Small copies use branch-minimized scalar/vector loads. Medium copies use paired SIMD loads/stores. Large copies check overlap, then copy forward with source alignment and 64-byte software-pipelined loops or backward for overlapping ranges, finishing with start/end 64-byte blocks.
- State and persistence behavior: Pure memory-copy routine; mutates only destination memory and no persistent state.
- Dependencies and integration points: Includes `asmdefs.h`, assumes ARMv8-a AArch64, Advanced SIMD, and unaligned accesses. Provides libc-compatible symbols for FoundationDB builds on AArch64.
- Risks: The single implementation must satisfy both `memcpy` non-overlap expectations and `memmove` overlap correctness. Boundary sizes and overlap direction are high-risk. ABI and CFI metadata must remain correct for profiling/unwinding.
- Test signals: Conformance tests should cover every boundary around 0, 3, 4, 8, 16, 32, 64, 96, 128, large sizes, all alignment combinations, forward/backward overlaps, and equality with libc behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/aarch64/memcpy.S -->
