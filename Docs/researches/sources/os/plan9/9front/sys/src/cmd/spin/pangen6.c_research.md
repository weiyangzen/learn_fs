# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen6.c

## Purpose

`pangen6.c` implements Spin's AST/FSM based static slicing analysis. It tracks def/use information over Promela statements, discovers channel aliases, marks data- and control-relevant transitions for a given property, reports redundant statements and variables, and suggests simplifications such as predicate abstraction, source/sink process merging, or avoiding buffer processes.

The file operates on Spin's internal `ProcList`, `FSM_state`, `FSM_trans`, `FSM_use`, `Element`, `Lextok`, `Symbol`, `Slicer`, and label structures declared elsewhere in the Spin codebase. It is analysis/generation support, not runtime verifier code.

## Main Data Structures

- `Pair` records candidate proper subgraph entry/exit pairs used by the dominator-based pruning logic.
- `AST` stores per-proctype analysis state: original process declaration, start state, FSM body, state/bitset counts, relevance flags, and subgraph pairs.
- `RPN` tracks proctype names referenced by remote references so those proctypes remain relevant.
- `ALIAS` records possible channel aliases, including origin bits for `RUN`, assignment, and receive-derived aliases.
- `ChanList` records sent channel-name references so receives at matching positions can conservatively infer aliases.
- Global lists such as `ast`, `slicer`, `rel_vars`, `chalias`, `chanlist`, `expl_par`, and `expl_var` carry analysis state across passes.

## Def/Use Analysis

The file uses four bit flags: `USE`, `DEF`, `DEREF_DEF`, and `DEREF_USE`. `def_use()` walks `Lextok` expression trees and classifies variable references in assignments, sends, receives, receive polls, channel predicates, arithmetic/logical expressions, `run`, `printf`, assertions, `eval`, and other Promela syntax. `name_def_use()` adds a unique `FSM_use` record to the current transition and recursively treats array/struct indices as uses. It also sets `Symbol.colnr` hints used later by `AST_suggestions()` for predicate-abstraction suggestions.

`AST_def_use()` recomputes each transition's `Val[0]`/`Val[1]` use lists from the current syntax tree, replacing earlier relation-use data with AST-aware def/use records that handle structs and indices more explicitly.

`AST_track()` is the public tracking entry point called from `main.c` when `export_ast` is enabled. It mirrors `def_use()` but adds slice criteria through `name_AST_track()` and `check_slice()`. It also detects an error case where the same receive operand is both defined and used in a receive statement.

## Channel Alias Analysis

Channel aliasing is conservative and covers:

- formal channel parameters bound through `run` calls (`AST_para()`, `AST_findrun()`, `AST_run_alias()`);
- local channels initialized from other channel names (`AST_par_chans()`);
- assignments to channel variables (`AST_other()`, `AST_haschan()`);
- channel names passed through channels, where sends and receives have compatible arity and parameter positions (`AST_sends()`, `AST_nrpar()`, `AST_ord()`).

`AST_trans()` computes the transitive closure of the alias relation. `AST_isini()` is used to distinguish freshly initialized channels from plain channel names when determining whether an alias match should make a transition relevant. `AST_aliases()` prints the resulting alias graph under verbose mode.

## Relevance Propagation

`AST_slice()` is the main orchestration function:

1. It marks proctypes referenced by remote references with `AST_dorelevant()`.
2. It computes def/use data for stored process FSMs.
3. It adds hidden assignment transitions for formal parameter passing and initialized variables through `AST_hidden()`.
4. It performs channel alias analysis.
5. It marks assertions as initially relevant with `AST_prelabel()`.
6. It iterates data dependence, dominator/subgraph pruning, and control dependence in `AST_criteria()`.
7. It dumps redundant statements/variables and prints suggestions.

`AST_relevant()` searches hidden parameter assignments, hidden variable initializers, and real transitions for definitions of a criterion variable. `def_relevant()` marks exact def matches and conservative channel alias matches. `AST_indirect()` marks a transition relevant, records the analysis round, and adds its used variables as new criteria.

`AST_tagruns()` marks proctypes relevant if they contain relevant statements or have relevant hidden parameters; it also marks `run` statements whose target proctype is relevant. Claims, trace processes, and the init process are always treated specially and retained.

## Control Dependence and Dominator Pruning

The control-dependence pass marks blockable channel operations and conditional guards that can affect reachability of relevant transitions. `AST_ctrl()`:

- premarks receive/send/condition/else transitions as control-relevant candidates;
- uses `FSM_critical()` to keep only candidates from which data-relevant transitions remain reachable;
- lifts marks through `if`, `do`, `atomic`, `d_step`, `non_atomic`, and `unless` structure;
- calls `AST_shouldconsider()` to add variables in relevant guards and blockable statements as criteria.

The dominator section computes forward and reverse dominance sets with word bitsets (`BPW`, `init_dom()`, `dom_perculate()`, `dom_forward()`). It then identifies proper subgraphs where internal code can be ignored for control dependence if the subgraph is clean. `curtail()` marks ineligible nodes that contain data-relevant edges, blocking non-branch edges, or branch points without `else`. `AST_checkpairs()`, `bad_scratch()`, and `mark_subgraph()` use recorded dominance pairs to mark irrelevant subgraphs.

## Reporting

`AST_dump()` performs a reachable DFS of each proctype FSM and `AST_edge_dump()` reports unmarked assignments, sends, receives, and conditions as redundant for the property. `AST_dump_rel()` marks relevant variables and reports unmarked global/local variables as redundant, excluding mtype constants, structs as containers, proctype symbols, and owned fields. `AST_suggestions()` suggests predicate abstraction for simple variables used only in conditionals and identifies proctypes that look like pure source, sink, or buffer processes.

## External Dependencies

The file relies on shared Spin globals such as `all_names`, `fsm_tbl`, `fsm`, `use_free`, `verbose`, and `o_max`; parser token definitions from `y.tab.h`; utility functions such as `emalloc`, `nn`, `comment`, `symvar`, `sputtype`, `Sym_typ`, `fatal`, and `non_fatal`; and FSM utilities such as `rel_use`.

## Notable Risks and Behaviors

- The analysis intentionally over-approximates channel aliases, especially channel names passed through receives.
- Array indices are treated as uses, while the variable name itself ignores index values for identity.
- Hidden formal-parameter and initializer assignments are modeled as synthetic `FSM_trans` records so data dependence can flow through generated semantics.
- Dominator and scratch marking uses `fsm_tbl` indexed by state numbers and temporarily swaps predecessor/successor edge lists; correctness depends on restoring these lists.
- The file prints directly to stdout for analysis results and diagnostics.
