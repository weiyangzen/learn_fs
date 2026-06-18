# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen2.c

Central Spin verifier code generator. It emits the generated `pan` verifier files: main C, header, transition table, forward-move code, backward-move code, and BFS_PAR support.

Key behavior:
- `gensrc` orchestrates generation of `pan.c`, `pan.h`, `pan.t`, `pan.m`, `pan.b`, and `pan.p`, or split variants for separate claim generation.
- Emits compile-time feature macros for model properties: claims, event traces, hidden variables, `_last`, priorities, sorted/random channel operations, `np_`, `unless`, embedded C, BFS, fairness, and partial-order reduction constraints.
- Walks every ready process with `putproc`, emits per-proctype transition arrays, source maps, reached arrays, loop-state arrays, and end-state definitions.
- Builds transition entries through `put_seq`, `put_sub`, `put_el`, and `case_cache`, including atomic/d_step handling, unless escapes, dead-link suppression, merge-chain support, case reuse, and transition-to-source mapping.
- Generates forward move code with `putstmnt` for Promela AST nodes: arithmetic/logical expressions, `run`, send/receive/poll, guards, `else`, assignments, assertions, print operations, remote references, embedded C, process deletion, and priority operations.
- Generates matching backward/undo hooks indirectly through case metadata and `pangen4.c`.
- Implements partial-order reduction classification with `Tpe`, `valTpe`, `has_global`, `q_cond` generation, xr/xs checks, timeout/youngest-process conditional safety, and detection of unsafe global references.
- Supports statement merging and multiple backup values through `multi_oval`, `multi_needed`, `CnT`, and dead-variable reset bookkeeping.
- Provides utility routines for claim process lookup, process reversal for initialization, name emission, run-expression validation, target resolution, and atomic-chain/global scanning.

Dependencies:
- Uses Spin parser/runtime structures from `spin.h` and `y.tab.h`: `ProcList`, `RunList`, `Sequence`, `Element`, `Lextok`, `Symbol`, `Queue`, and label/state metadata.
- Includes template/string fragments from `pangen2.h`, `pangen4.h`, `pangen5.h`, and `pangen7.h`.
- Relies heavily on global generation flags and helper functions from the rest of Spin: `ready`, `disambiguate`, `genheader`, `genaddproc`, `genother`, `genaddqueue`, `gencodetable`, `putsrc`, `dumpsrc`, `comment`, `putcode`, `undostmnt`, `any_undo`, `spit_recvs`, and embedded-C plunking helpers.

Research notes:
- This file is the main behavioral bridge from Promela AST/FSM elements to executable verifier C.
- Correctness depends on synchronized forward/backward code generation and on preserving transition ids, source-state numbers, and backup-value ordering.
- Many paths are controlled by generated-code compile macros; changes need testing across normal DFS, BFS, BFS_PAR, bitstate, collapse, TRIX, separate claim, rendezvous, and reduction modes.
