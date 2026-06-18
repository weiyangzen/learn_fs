# sources/test-tools/crashmonkey/ace/specific_generator_scripts/workload_seq3.py

## Purpose

`workload_seq3.py` is the third j-lang to C++ translator variant. It is close to `workload_seq2.py` but adds explicit j-lang support for separate `msync` and `munmap` operations, changes mmap write generation so mappings can stay live across operations, and emits a fixed 256 KiB mapping for mmap workloads. It supports workloads where mmap writes and later sync/unmap operations are distinct crash points.

## Important APIs, Types, and Functions

- CLI arguments mirror seq1/seq2.
- `insertMsync(contents, option, line, index_map, method)` emits `cm_->CmMsync(filep_<file> + offset, length, MS_SYNC)`.
- `insertMunmap(contents, option, line, index_map, method)` emits `cm_->CmMunmap(filep_<file>, 262144)`.
- `insertWrite` handles buffered write, direct write, and mmapwrite. For mmapwrite, it fallocates, maps 262144 bytes once per file, writes bytes into `filep_<file> + offset`, and leaves msync/munmap to explicit later lines.
- `insertFunctions` dispatches the expanded command set, including `msync` and `munmap`.
- `main` performs the same base scan, copy, and section-driven insertion process as seq2.

## Control Flow

The translation flow is unchanged from seq2 until operation dispatch. When a j-lang `mmapwrite` is encountered, the generated C++ writes into a shared mapping and does not immediately `msync` or unmap. Later `msync` and `munmap` j-lang lines can be placed at specific points in the run section and get their own generated snippets. This enables crash tests that distinguish dirty mapped data, msync persistence, and unmap behavior.

## State and Persistence Behavior

`redeclare_map` tracks mmap offsets and direct-I/O variables to avoid duplicate declarations. Because mmap state now persists across j-lang operations in the generated C++ file, `filep_<file>` becomes a generated runtime state variable whose lifetime is controlled by explicit `munmap` lines rather than by `mmapwrite` itself. The persistent output remains one generated `.cpp` file.

## Dependencies and Integration Points

The generated C++ depends on the same CrashMonkey wrapper APIs as seq2 plus explicit `CmMsync` and `CmMunmap` calls. It is the natural downstream translator for write-intensive sequence generators that model mmap persistence separately from the write operation. Generated tests integrate with the Makefile via the generated workload or sequence test shared-object rules.

## Risks and Edge Cases

- Python 2 only.
- The generated mmap declaration is embedded as one long string with limited newlines, which can make line-count updates and compiler diagnostics harder to reason about.
- Fixed 262144-byte mappings may be too large or too small for generated ranges if future generators expand offsets.
- `insertMunmap` always unmaps 262144 bytes and does not guard against repeated unmaps.
- As with seq2, generated filenames can be surprising when `test_file` includes directory prefixes.
- Offset-map declarations are keyed by `moffset_<file>`, but file pointer lifetime is keyed indirectly; malformed j-lang can emit `msync` before the first `mmapwrite`.

## Test Signals

Strong tests include j-lang fixtures with `mmapwrite`, `msync`, and `munmap` in different orders, generated C++ compilation, and CrashMonkey execution that verifies consistency changes only after `msync` where expected. Regression tests should verify direct writes still close/reopen with O_DIRECT/O_SYNC and that seq2-to-seq3 differences are intentional rather than insertion drift.
