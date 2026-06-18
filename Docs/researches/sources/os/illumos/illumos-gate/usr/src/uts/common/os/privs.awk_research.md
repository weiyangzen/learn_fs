# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/privs.awk

## Purpose

`privs.awk` is the generator for illumos privilege metadata. From a privilege definition input, it emits private kernel constants, public privilege-name constants, the C privilege name/metadata table, and `/etc/security/priv_names` explanatory text.

Read completely: 404 lines.

## Main Responsibilities

- Parses privilege definitions, optional privilege category keywords, set definitions, comments, and pragmas.
- Generates `<sys/priv_const.h>` with private numeric constants, set constants, set sizes, maximum privilege count, generated assertions, and externs for generated tables.
- Generates `os/priv_const.c` with packed privilege/set name strings, `priv_impl_info_t`, `priv_info_names_t`, `priv_basic`, `priv_info`, counters, and string slack for runtime allocation.
- Generates `<sys/priv_names.h>` with public `PRIV_*` string constants and comments.
- Generates `/etc/security/priv_names` with privilege explanations.

## Important State And Variables

- `npriv`, `nset`: counts of parsed privileges and privilege sets.
- `privbytes`, `setbytes`: packed string storage sizes.
- `slack`: extra privilege slots reserved for runtime-allocated privileges.
- Arrays `privs`, `sets`, `privind`, `setind`, `pdef`, `sdef`, `privcmt`, `setcmt`, `privncmt`: accumulated output fragments and metadata.
- Output variables supplied by the makefile: `privhfile`, `pubhfile`, `cfile`, and `pnamesfile`.

## Control Flow And Algorithms

The `BEGIN` block initializes counters and canned comments for each generated output.

Privilege lines matching `privilege` optionally record category membership, normalize `PRIV_*` names to lowercase runtime names, compute packed-string offsets, build aligned `#define` fragments, collect following comments, and increment `npriv`.

Set lines matching `set` normalize names to initial-cap strings, record offsets and define fragments, collect following comments, and increment `nset`.

`INSERT COMMENT` writes generated-file warnings to selected outputs. `#pragma` lines are preserved in generated C/headers and transformed for the privilege-names text output. Ordinary comments are mostly skipped or converted for the names file.

The `END` block validates that at least one output was selected, computes privilege set size and maximum runtime string storage, then writes each requested file. The generated C file uses one packed `struct _info` containing implementation metadata, set names, privilege names, and the basic privilege set. Header generation emits constants and public string mappings. Names-file generation emits each privilege and accumulated description.

## Dependencies And Integration

- Run by the illumos build to generate kernel-private and public privilege artifacts.
- The generated `priv_const.c` is consumed directly by `priv.c` and credential code.
- Category assertions generated from keyworded privilege lines become macros such as generated `PRIV_*_ASSERT(set)` forms.

## Notable Risks And Invariants

- Numeric privilege constants are explicitly private and may be renumbered; public consumers must use names.
- Runtime allocation capacity depends on `slack`, `setsize`, and computed `maxprivbytes`.
- Input names must follow `PRIV_*` conventions because the script strips the prefix and computes lengths from it.
- The generated packed strings and offset fields must remain consistent with `priv_impl_info_t` consumers.

## Research Relevance

This script defines the generated privilege universe that kernel access checks use. It is relevant when tracing a named privilege from public headers into numeric kernel privilege-set operations.
