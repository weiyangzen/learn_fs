# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen1.c

## Purpose

`pangen1.c` is part of Spin’s verifier generator. It writes generated verifier C code, mainly into `pan.c`, `pan.h`, and related generated files through global output streams `tc`, `th`, and `tt`.

It combines model metadata, process lists, queues, labels, variable declarations, and large string-template fragments from `pangen1.h`, `pangen3.h`, and `pangen6.h`.

## Main Responsibilities

- Generates verifier headers and state-vector layout.
- Emits process type structs and queue structs.
- Emits process and channel initialization code.
- Emits claim, progress, accept, stop, visible, and reached-state tables.
- Emits helpers for global/local variable printing.
- Emits queue runtime functions for generated verifier code.
- Emits support for sorted/random receive, rendezvous, TRIX compression, BFS/DFS modes, multi-claim models, and provided clauses.

## Output Streams

- `th`: generated header-like verifier declarations and structs.
- `tc`: generated verifier implementation body.
- `tt`: generated transition/provided support, especially `provided(...)`.

The file’s behavior is mostly `fprintf` and `ntimes` template expansion over those streams.

## Key Generation Paths

`genheader()` writes foundational verifier definitions:
- Word size and channel counts.
- `NCORE` defaults.
- User-defined names.
- Process names and process type categories.
- `P<n>` process structs.
- Multi-claim wrapper process if needed.
- State-vector `State`.
- TRIX-specific state storage structures.
- Hidden variables and predefined write-only `_`.

`genaddproc()` writes:
- TRIX channel re-marking helper.
- `addproc(...)`.
- Optional `provided(...)`.
- Multi-claim initialization.
- `np_` predefined process.
- Per-proctype initialization cases.

`genother()` writes:
- State-table code fragments.
- Label-derived arrays for stop/progress/accept states.
- Reachability reporting setup.
- `iniglobals(...)`.
- Main verifier body templates such as DFS/BFS support.

`genaddqueue()` writes:
- Queue type definitions `Q<n>`.
- Queue metadata arrays `q_flds` and `q_max`.
- `addqueue`.
- `qsend`, `qrecv`, `q_len`, `q_full`, and queue size helpers.
- Optional `Q_has` for random receive polling.

## Important Functions

- `reverse_names`, `reverse_types`: emit process metadata in reverse list order.
- `blog`: computes enough bit width for generated bitfields.
- `genheader`: top-level state-vector and proctype header generation.
- `genaddproc`: add-process generation and process initialization dispatch.
- `genother`: state tables, reachability, globals, and main verifier body generation.
- `gensvmap`: emits state-vector map template.
- `end_labs`: maps labels to `stopstate`, `progstate`, `accpstate`, and `visstate`.
- `ntimes`: expands template arrays, substituting an index into repeated `%d` placeholders.
- `checktype`: warns that integer-like declarations could be narrowed to `bit` or `byte`.
- `dolocal`, `doglobal`: enumerate model variables in declaration/type order for initialization, logging, or struct emission.
- `c_chandump`, `c_var`, `c_splurge`, `c_wrapper`: generate runtime variable/channel dump helpers.
- `dohidden`: emits hidden globals and predefined `_`.
- `do_var`, `do_init`: generate initialization/logging code for scalar, array, struct, and channel variables.
- `put_ptype`: emits process struct declarations and `Air<n>` size macros.
- `tc_predef_np`: emits the built-in `np_` process metadata.
- `multi_init`: emits multi-never-claim selection initialization.
- `put_pinit`: emits initialization case for a proctype.
- `huntstart`, `huntele`: find executable control-flow entry states through gotos, unless blocks, and atomic/d_step structure.
- `typ2c`: maps Promela types to generated C fields.
- `qlen_type`: picks compact queue length storage type.
- `genaddqueue`: emits generated queue runtime code.

## Data and Model Coupling

The file depends on global parser/generator state:
- Process list: `rdy`, `nrRdy`, `Pid`.
- Queue list: `qtab`, `ltab`, `nqs`.
- Labels: `labtab`.
- Symbols: `all_names`, `Fname`, `lineno`.
- Claims and traces: `nclaims`, `claimnr`, `eventmapnr`.
- Feature flags: `separate`, `old_scope_rules`, `has_sorted`, `has_random`, `has_provided`, `has_io`, `has_state`.

Generated code depends on many symbols emitted elsewhere, including transition tables, state vector helpers, queue pointer helpers, C code fragments, and templates from other `pangen*.h` files.

## Notable Behavior

- `separate` controls whether normal processes and claims are generated together or split.
- Multi-claim support replaces concrete claims in the state vector with an aggregate claim process storing active claim type/state/index and per-claim current states.
- Claims are not allowed to define locals; `dolocal` reports this as an error for `N_CLAIM`.
- Channel initialization calls `qmake`, then emits either a queue id or `addqueue(...)` depending on whether a dynamic channel must be created in generated verifier state.
- Queue field widths are compacted based on Promela field types; unsupported channel field specs are fatal.
- State labels inside `atomic`/`d_step` blocks produce warnings because they may be invisible.
- `provided` clauses are emitted as a generated switch over proctype/state.

## Risks and Maintenance Notes

This file is a code generator built around `fprintf` templates and global mutable state. Small changes can affect generated C in many compile modes.

The generated verifier has many mutually interacting options: BFS, TRIX, multi-core, bitstate, compression, hash compaction, fairness, bounded context switching, claims, randomization, and rendezvous. Changes to emitted structs or queue layouts must stay synchronized with generated runtime functions and template assumptions in `pangen1.h`.

Because it emits C identifiers and string fragments from model symbols, correctness depends on parser-side sanitization and name mangling.

## Filesystem Relevance

No filesystem algorithm is implemented. The generated verifier can emit and read trail files, stack spill files, and temporary BFS disk files through template code, but this file itself is generator logic.
