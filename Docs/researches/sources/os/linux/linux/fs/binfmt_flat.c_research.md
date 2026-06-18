# File Research: sources/os/linux/linux/fs/binfmt_flat.c

## Purpose
Implements the Linux `bFLT` flat binary loader, primarily for NOMMU/embedded systems, with optional compressed FLAT support and relocation processing.

## Registration
- `flat_format` provides `load_binary = load_flat_binary`.
- Registered at `core_initcall(init_flat_binfmt)`.

## Format State
- `struct lib_info` stores one supported library/program slot:
  - code/data/brk starts
  - text length
  - entry point
  - build date
  - loaded flag
- `MAX_SHARED_LIBS` is 1 in this implementation.
- Constants:
  - `FLAT_DATA_ALIGN`
  - `FLAT_STACK_ALIGN`
  - `RELOC_FAILED`
  - `UNLOADED_LIB`

## Stack Table Setup
- `create_flat_tables()` builds argc, argv, envp, and optional argvp/envp pointers on the user stack, updating `arg_start/end` and `env_start/end`.

## Optional Compressed FLAT
Under `CONFIG_BINFMT_ZFLAT`:
- `decompress_exec()` parses gzip headers, validates unsupported flags, inflates file data using zlib, and writes into destination memory.

## Relocation
- `calc_reloc()` maps relocation offsets into runtime text or data addresses and sends `SIGSEGV` on invalid relocation.
- `old_reloc()` supports legacy flat relocation records under `CONFIG_BINFMT_FLAT_OLD`.
- `skip_got_header()` skips RISC-V GOT PLT headers before GOT relocation.
- `load_flat_file()` performs:
  - header parsing and magic/version validation
  - sanity checks for large/corrupt sizes
  - data rlimit check
  - `begin_new_exec()`, personality setup, and memory mapping/allocation
  - optional ROM text mapping for NOMMU
  - optional compressed code/data loading
  - code/data/brk/stack mm field setup
  - GOT relocation
  - relocation table processing
  - instruction-cache flush
  - zeroing bss, brk, and stack area

## Main Exec Flow
`load_flat_binary()`:
1. Computes required stack length including argv/envp pointer arrays and, on NOMMU, argument string pages.
2. Calls `load_flat_file()`.
3. Writes library data-start pointers or `UNLOADED_LIB` sentinels.
4. Sets the active binary format.
5. Sets up arg pages or NOMMU stack and creates flat tables.
6. Applies platform initialization if present.
7. Finalizes exec and starts the thread at the flat entry point.

## Security and Robustness Notes
- Validates magic, version, compression support, and high bits of size fields.
- Enforces `RLIMIT_DATA` against data plus bss.
- Uses `read_code()`, `copy_to_user()`, and relocation helpers with error checks.
- Relocation failures abort exec or signal the current task for invalid offsets.
