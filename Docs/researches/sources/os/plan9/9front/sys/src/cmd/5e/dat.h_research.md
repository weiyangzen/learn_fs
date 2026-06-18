# File Research: sources/os/plan9/9front/sys/src/cmd/5e/dat.h

This header defines the process, segment, and fd-table state for `5e`.

Key contents:
- Type declarations for `Process`, `Segment`, `Fdtable`, and `Fd`.
- Constants:
  - stack size, process name max, note ring length, segment count, floating register count,
  - CPSR flag bits `flN`, `flZ`, `flC`, `flV`, and `FLAGS`,
  - segment IDs `SEGTEXT`, `SEGDATA`, `SEGBSS`, `SEGSTACK`.
- `Process` contains:
  - process-list links and pid/name/path,
  - segment array,
  - LL/SC emulation state,
  - 16 general registers and CPSR,
  - FPSR and long-double FP register file,
  - per-process error buffer,
  - OCEXEC fd table,
  - note handler state, jump buffer, queued notes, and note ring indexes.
- Defines global VFP flag and thread-private process access macro `P`.
- `Segment` contains refcount, flags, optional lock, address range, backing data, and shared data ref.
- `Fd` contains lock, refcount, OCEXEC bitmap, and bitmap length.
- Debug compile-time macros are all currently disabled: `fulltrace`, `havesymbols`, `ultraverbose`, and `systrace`.

Dependencies and interactions:
- Included by every `5e` source file.
- The `P` macro depends on Plan 9 thread private storage.

Research relevance:
- Central runtime data model for the emulator.

Risk notes:
- `Process.notes` is declared as `char notes[ERRMAX][NNOTE]`, while indexing treats the outer dimension like the note slot. This is large enough but dimensionally surprising.
- Segment sharing/copying uses separate segment refcount and backing-data refcount.
