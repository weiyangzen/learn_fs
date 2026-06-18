# File Research: sources/os/plan9/9front/sys/src/cmd/spin/guided.c

`guided.c` replays verifier trail files against Spin’s interpreted model graph. It is used for guided simulations/error-trail replay, including optional xspin/two-column/MSC-style output.

`match_trail()` locates a trail file by explicit `-k` name or by trying `.trail`/`.tra` variants of the model filename, warns if the model is newer, enables timeout handling, calls `hookup()` to resolve compound statement starts, then reads trail records as `depth:process:state`. Special negative depth records start claims, mark merged-statement mode, or print cycle-start markers.

For each trail step it finds the matching `Element` by global `Seqno`, maps the verifier process number onto the active `RunList`, updates `X->pc`, executes or tests transitions with `eval_sub()`, handles merged transitions, and prints process/statement/value output according to verbosity. `D_STEP` replay walks internal substeps until it reaches the enclosing next state.

`find_min()` and `find_max()` compute valid statement-number ranges for a process sequence, including nested compound sequences, to diagnose stale or mismatched trails. `lost_trail()` dumps remaining trail records when replay cannot match a step. `pc_value()` implements the Promela `pc_value()` helper over the active run list.

Important caveats: embedded C code is explicitly not executed during this kind of replay, so variable values can be inaccurate; stale trails are detected only by file modification time; and replay depends on generated statement numbers matching the current parsed model.
