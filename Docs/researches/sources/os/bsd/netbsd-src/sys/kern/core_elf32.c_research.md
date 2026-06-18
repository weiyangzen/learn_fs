# File Research: sources/os/bsd/netbsd-src/sys/kern/core_elf32.c

## Purpose
Implements ELF32 core dump generation; also serves as the template included by `core_elf64.c` when `ELFSIZE` is 64.

## Main Interfaces
- `ELFNAMEEND(real_coredump)()` builds ELF headers, program headers, PT_NOTE contents, and writes process memory segments.
- `ELFNAMEEND(coredump_getseghdrs)()` converts UVM dump segments into `PT_LOAD` program headers and trims trailing zero pages where possible.
- `ELFNAMEEND(coredump_notes)()` gathers process, auxv, and per-LWP notes.
- `ELFNAMEEND(coredump_note)()` saves LWP status, integer registers, optional FP registers, and machine-dependent notes.
- `ELFNAMEEND(coredump_savenote)()` serializes aligned ELF notes into linked buffers.

## Implementation Notes
The dump takes three map passes conceptually: count segments, build headers, then write segment data. It uses module hooks for UVM map walking/counting and coredump I/O, allowing the generic core code to call implementation-specific writers.

## Dependencies
Uses ELF exec definitions, process/register/ptrace APIs, UVM coredump hooks, coredump module hooks, kauth credentials, and optional netbsd32 support.
