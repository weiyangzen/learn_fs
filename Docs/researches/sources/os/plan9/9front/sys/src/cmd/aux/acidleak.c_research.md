# File Research: sources/os/plan9/9front/sys/src/cmd/aux/acidleak.c

Heap leak analyzer/visualizer for ACID-generated allocation traces.

Input model:
- Parses stdin lines such as `data <addr> <val> <type>`, `block <addr> <size> <w0> <w1> ...`, `free ...`, and `range alloc <start> <end>`.
- Stores allocation blocks and pointer-like data records, sorts them by address, and traces reachability.

Important behavior:
- `findblock()` and `finddata()` binary-search sorted arrays.
- `markblock()` marks allocated blocks reachable from data values that point near block headers, recursing through contained data.
- Default output prints unmarked, non-free blocks as likely leaks.
- `-b` emits a Plan 9 bitmap (`m8`) showing allocated, leaked, free, header, and padding regions with color codes.
- `-r` controls bitmap resolution; `-x` controls bitmap width.

Filesystem relevance:
- Consumes textual memory dumps and can emit image-format leak maps; useful for diagnosing long-running file servers or kernel/user processes with ACID data.
