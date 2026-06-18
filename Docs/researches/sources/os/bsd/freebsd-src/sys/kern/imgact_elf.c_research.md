# File Research: sources/os/bsd/freebsd-src/sys/kern/imgact_elf.c

## Summary
Implements FreeBSD ELF image activation and ELF core dump generation for the selected `__ELF_WORD_SIZE`. It handles ELF header validation, brand detection, interpreter loading, VM segment mapping, ASLR/W^X policy, aux vector construction, process ABI setup, and ELF-format core notes/segments.

## Main Responsibilities
- Maintains ELF brand registration and selection for FreeBSD, GNU/kFreeBSD, fallback brands, interpreter paths, OSABI fields, legacy branding, and ABI notes.
- Validates ELF headers and program headers, including class/data/version/machine, program-header count, segment alignment, PT_INTERP, PT_GNU_STACK, PT_PHDR, and PT_NOTE constraints.
- Maps executable and interpreter PT_LOAD sections into a fresh process VM space, handling partial pages, non-page-aligned file offsets, bss, copy-on-write, no-core mappings, executable text references, and resource limits.
- Implements ASLR and PIE base selection, stack/shared-page randomization flags, `MAP_WXORX`, and feature-control notes.
- Builds ELF auxargs and stack fixup data.
- Generates ELF core dumps with PT_NOTE, PT_LOAD entries, register notes, procstat notes, and optional compression.

## Key Exec APIs
- `__elfN(check_header)()` validates basic ELF identity and ensures at least one brand exists for the machine.
- `__elfN(get_brandinfo)()` selects ABI brand by note, OSABI, legacy header brand, header callback, interpreter path, or fallback brand.
- `__elfN(load_section)()` maps one PT_LOAD segment, including initialized data and zero-fill/bss.
- `__elfN(load_sections)()` maps all loadable segments and reports the first base address.
- `__elfN(load_file)()` loads an interpreter/shared object by pathname.
- `__CONCAT(exec_, __elfN(imgact))()` is the main ELF image activator.
- `__elfN(freebsd_copyout_auxargs)()` emits aux vector entries.
- `__elfN(freebsd_fixup)()` writes `argc` on the user stack.
- `EXEC_SET(ELF_ABI_ID, __elfN(execsw))` registers the activator.

## Key Core-Dump APIs
- `__elfN(coredump)()` sizes segments/notes, checks core limits/accounting, sets up compression, writes headers/notes, and outputs dumpable VM segments.
- `each_dumpable_segment()` filters VM map entries for core dumping.
- `__elfN(prepare_notes)()` builds the note list.
- `__elfN(puthdr)()` emits ELF and program headers, including extended numbering when needed.
- `__elfN(register_note)()`, `register_regset_note()`, `populate_note()`, and `putnote()` manage note sizing and serialization.
- Note emitters cover `PRPSINFO`, `PRSTATUS`, FP registers, thread metadata, ptrace LWP info, procstat proc/files/vmmap/groups/umask/rlimit/osrel/psstrings/auxv/kqueues.

## Important Exec Behavior
The activator accepts `ET_EXEC` and supported `ET_DYN` binaries. It rejects too many program headers, wraparound in program-header ranges, invalid segment alignment, multiple interpreters, invalid stack permissions, unknown brands, and unsupported executable shared objects.

For setid binaries it clears user ASLR and W^X preference flags. ASLR decisions combine ABI support, sysctls, process flags, PIE state, and FreeBSD feature-control notes. If ASLR is enabled, it randomizes PIE base, `anon_loc`, stack, and optionally shared-page placement.

The code unlocks the executable vnode around `exec_new_vmspace()` to avoid vnode/VM deadlocks while relying on executable text references to prevent modification. It relocks before loading sections.

## Important Core-Dump Behavior
Core dumping sizes all dumpable segments first, computes header/note size, charges RACCT core usage, rejects dumps above the limit, optionally compresses, and then writes PT_NOTE plus page-aligned PT_LOAD segment contents.

Dumpable segment filtering excludes inaccessible mappings unless `SVC_ALL` is requested, honors `MAP_ENTRY_NOCOREDUMP`, ignores submaps and fictitious backing objects, and supports a legacy mode that dumps only read/write mappings.

## State and Tunables
Important sysctls/tunables include `fallback_brand`, `debug.elf*.legacy_coredump`, `nxstack`, `vdso`, `read_exec` for 32-bit x86, `pie_base`, ASLR enablement knobs, `sigfastblock`, `allow_wx`, and program-header count limit `phnums`.

## Risks
This file is security-critical. It parses untrusted executable headers, maps user VM, applies ABI policy, and emits core files. High-risk areas include integer overflow checks, vnode lock dropping/relocking, text-reference accounting, feature-control note parsing, W^X/ASLR policy precedence, and note-size prediction for coredumps.
