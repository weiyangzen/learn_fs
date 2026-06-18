# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_notes.h

This small header defines Sun-specific ELF note naming and a note type for page-size hints.

Key contents:
- ELF note owner/name string:
  - `ELF_NOTE_SOLARIS`
- Note type:
  - `ELF_NOTE_PAGESIZE_HINT`

Dependencies:
- No includes.
- Uses C++ guards.

Research notes:
- `ELF_NOTE_PAGESIZE_HINT` describes the desired page size for ELF `PT_LOAD` segments; the descriptor is one word containing the desired page size.
- This is a small ABI helper for ELF producers/consumers that understand Solaris notes.
