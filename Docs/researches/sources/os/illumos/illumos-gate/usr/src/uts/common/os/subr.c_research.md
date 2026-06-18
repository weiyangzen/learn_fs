# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/subr.c

## Purpose

Provides miscellaneous low-level kernel helper routines used across illumos: default device entry points, unused major allocation, device-number conversion, suboption parsing/building, BCD lookup tables, hot patching of kernel text, non-executable-data execution logging, memlist range checking, `on_trap` cleanup, and zone-aware node-name lookup.

## Main Responsibilities

- Supply `nodev()` and `nulldev()` placeholders for device switch tables.
- Allocate fallback/unused major device numbers with `getudev()`.
- Convert between native `dev_t` and 32-bit `dev32_t` encodings.
- Provide 32-bit-only `min`/`max`/`umin`/`umax` compatibility functions.
- Parse and append comma-separated suboptions.
- Export byte-to-BCD and BCD-to-byte lookup tables.
- Patch kernel text instructions by temporarily mapping physical pages writable.
- Report attempted execution from stack or other non-executable user data.
- Test whether an address range is fully contained in a `memlist`.
- Pop current-thread `on_trap()` protection.
- Return global or zone-local nodename.

## Key Entry Points

- `nodev()`
  Returns `ENXIO`, and when called from an LWP stores it in `lwp_error`.

- `nulldev()`
  Returns success for unused device operations.

- `getudev()`
  Allocates a major number above `devcnt` when possible; if exhausted, scans `devnamesp` backward for an unused slot and marks it `DN_TAKEN_GETUDEV`.

- `cmpldev(dev32_t *dst, dev_t dev)`
  Compresses native device numbers to 32-bit encoding, returning failure if major/minor cannot fit.

- `expldev(dev32_t dev32)`
  Expands 32-bit device numbers back to native `dev_t`, preserving `NODEV`.

- `getsubopt(char **optionsp, char * const *tokens, char **valuep)`
  Kernel implementation of `getsubopt(3C)`-style comma/equal option parsing.

- `append_subopt(const char *buf, size_t len, char *str, const char *opt)`
  Appends an option string with comma separation, failing if the target buffer lacks space.

- `hot_patch_kernel_text(caddr_t iaddr, uint32_t new_instr, uint_t size)`
  Hot-patches a 1-, 2-, or 4-byte kernel instruction, handling page-straddling writes and instruction-cache synchronization.

- `report_stack_exec(proc_t *p, caddr_t addr)`
  Logs attempts to execute stack or non-executable user data when logging is enabled.

- `address_in_memlist(struct memlist *mp, uint64_t addr, size_t len)`
  Returns whether `[addr, addr + len)` is contained in one memlist segment.

- `no_trap(void)`
  Pops the top `t_ontrap` frame, with SPARC deferred-error barrier handling.

- `uts_nodename(void)`
  Returns `utsname.nodename` without a current process, otherwise the current zone’s nodename.

## Important Data

- `udevlock`
  Serializes `getudev()` allocation and sparse devnames fallback reuse.

- `byte_to_bcd[256]`, `bcd_to_byte[256]`
  Lookup tables for BCD conversion.

- `devnamesp`, `devcnt`
  Device major namespace inspected by `getudev()`.

- `heap_arena`, `kas`, HAT mappings
  Used by `hot_patch_kernel_text()` to map kernel text pages writable without changing original virtual mapping protections.

## Locking and Synchronization

- `getudev()` uses `udevlock` and individual `devnamesp[i].dn_lock` entries while scanning/reusing sparse major slots.
- `hot_patch_kernel_text()` page-locks the affected kernel address range, maps the backing PFNs into a temporary writable virtual range, writes the instruction, issues memory/icache synchronization, unlocks pages, unloads the mapping, and frees virtual space.
- `no_trap()` mutates only the current thread’s `t_ontrap` stack.

## Error and Edge Handling

- `getudev()` warns when it reuses a sparse major number and returns `DDI_MAJOR_T_NONE` only if no usable number exists.
- `cmpldev()` sets output to `NODEV32` on overflow as a defensive value for callers.
- `append_subopt()` includes room for a comma and the null terminator in its bounds check.
- `hot_patch_kernel_text()` panics on unsupported patch sizes and explicitly supports instruction writes that straddle a page boundary.
- `report_stack_exec()` rate-slows via a short delay after logging.

## External Dependencies

Device switch tables and `devnamesp`, DDI major/minor encodings, VM/HAT/page locking, instruction-cache synchronization, process credentials, zones, `utsname`, `ontrap`, and memlist structures.

## Research Notes

This file is small but low-level. The most sensitive code is `hot_patch_kernel_text()`, where size/alignment assumptions, temporary writable mappings, page-straddling behavior, and icache synchronization are correctness-critical. `getudev()` is also boot-sensitive because it is designed to succeed even when the major-number namespace is sparse or near exhaustion.
