# File Research: sources/os/bsd/netbsd-src/sys/kern/kgdb_stub.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kgdb_stub.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements the machine-independent KGDB remote protocol stub for kernel debugging over a device such as a serial line.

## Purpose And Main Interfaces

- Attachment:
  - `kgdb_attach`
- Trap handling and command loop:
  - `kgdb_trap`
- Miscellaneous:
  - `kgdb_disconnected`
  - weak `kgdb_entry_notice`
  - `kgdb_voidop`

## Key State

- `kgdb_dev`, `kgdb_rate`, `kgdb_active`, `kgdb_debug_init`, and `kgdb_debug_panic` configure global KGDB behavior.
- `kgdb_getc`, `kgdb_putc`, and `kgdb_ioarg` are installed by a device driver through `kgdb_attach`.
- `kgdb_recover` points to a recovery label while the KGDB command loop is active.
- `buffer[KGDB_BUFLEN]` is the packet buffer.
- `gdb_regs[KGDB_NUMREGS]` caches register state in GDB wire format.

## Control Flow

- `kgdb_attach` installs character I/O callbacks and callback argument.
- `kgdb_waitc` spins until the input callback returns a character.
- `kgdb_send` emits `$payload#checksum` packets and retries until it receives an acknowledgement other than bad-packet.
- `kgdb_recv` waits for a start marker, accumulates payload and checksum, validates packet length/checksum, acknowledges good/bad packets, and strips optional sequence prefixes.
- `kgdb_trap` is entered from trap handling:
  - ignores traps if KGDB is not configured.
  - clears single-step state.
  - calls optional `db_trap_callback`.
  - recovers unexpected traps during KGDB memory access with `longjmp`.
  - handles first breakpoint entry by advancing PC and marking KGDB active.
  - sends signal packets on later traps.
  - converts MD registers into `gdb_regs`.
  - loops processing remote commands until continue/step/detach/kill.
- Supported commands include signal query, register read/write, memory read/write, detach/kill, continue, and single-step.
- Memory access commands check `kgdb_acc` before using `db_read_bytes` or `db_write_bytes`.

## Helper Functions

- `kgdb_copy` is a local byte copy routine so `bcopy` can be debugged.
- `digit2i`, `i2digit`, `mem2hex`, `hex2mem`, and `hex2i` implement remote protocol conversions.
- `kgdb_disconnected` currently always returns `1`.

## Concurrency And Invariants

- The command loop assumes a stopped-kernel debugging context.
- Packet I/O is synchronous and blocking.
- `kgdb_recover` is only non-null while inside the command loop.
- MD hooks provide breakpoint PC fixup, register conversion, single-step control, signal mapping, and memory-access validation.

## Risks And Edge Cases

- Packet receive rejects overlong packets and malformed hex.
- Register writes require the whole converted packet to terminate exactly.
- Memory reads use the upper half of `buffer` as a temporary raw byte area before hex encoding.
- Detach and kill both clear `kgdb_active`, clear single-step, send `OK`, and leave the loop.
