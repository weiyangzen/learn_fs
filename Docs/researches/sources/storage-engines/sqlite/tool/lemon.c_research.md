# sources/storage-engines/sqlite/tool/lemon.c

## Purpose
`lemon.c` is SQLite's bundled Lemon LALR(1) parser generator. It reads a Lemon grammar file, optionally preprocesses `%ifdef`/`%ifndef` regions, builds grammar symbols/rules/states/follow sets/actions, resolves conflicts, compresses and renumbers parser tables, then emits generated parser C, token headers, reports, and optionally an SQL description of grammar tables. It is a single-file amalgamation of Lemon modules (`action`, `acttab`, `build`, `configlist`, `main`, `option`, `parse`, `plink`, `report`, `set`, and generated table helpers).

## Important APIs, Types, and Functions
- Core model types: `struct lemon` holds whole-generator state and output options; `struct symbol` represents terminals, nonterminals, and multiterminals; `struct rule` represents productions and reduce code; `struct config` represents LR configurations and follow sets; `struct state` represents generated automaton states; `struct action` represents shift/reduce/accept/error actions.
- Memory and utility layer: `lemon_malloc`, `lemon_calloc`, `lemon_realloc`, `lemon_free`, and `lemon_free_all` track allocations in `memChunkList`; `lemon_sprintf`/`lemon_vsprintf` implement a narrow formatter used by generated paths and diagnostics.
- Build pipeline: `FindRulePrecedences`, `FindFirstSets`, `FindStates`, `FindLinks`, `FindFollowSets`, and `FindActions` implement parser construction.
- State/config helpers: `Configlist_add`, `Configlist_addbasis`, `Configlist_closure`, `State_insert`, `State_find`, `Configtable_insert`, and `Configtable_find` de-duplicate configurations and states through generated hash-table code.
- Parser for grammar input: `Parse`, `preprocess_input`, `eval_preprocessor_boolean`, and `parseonetoken` scan the grammar file, build rules, process directives such as `%name`, `%type`, `%fallback`, `%wildcard`, `%token_class`, `%destructor`, and capture user code blocks.
- Reporting and output: `ReportOutput`, `ReportTable`, `ReportHeader`, `Reprint`, `CompressTables`, `ResortStates`, `translate_code`, `emit_code`, and `emit_destructor_code` produce `.out`, `.c`, `.h`, and optional `.sql` outputs.
- Table construction: `acttab_alloc`, `acttab_action`, `acttab_insert`, `compute_action`, and `minimum_size_type` generate compact `yy_action`, `yy_lookahead`, offset, and default-action tables.

## Control Flow
1. `main()` parses command-line options with the local option framework. Notable switches include `-b`, `-c`, `-d`, `-D`, `-E`, `-g`, `-m`, `-l`, `-p`, `-q`, `-r`, `-s`, `-S`, `-T`, and `-U`.
2. It initializes string, symbol, and state tables, creates the end marker symbol `$`, and calls `Parse(&lem)`.
3. `Parse()` reads the entire grammar into memory, runs `preprocess_input()`, then tokenizes identifiers, string literals, C code blocks, comments, `::=`, aliases, precedence marks, and one-character operators. Each token feeds `parseonetoken()`.
4. `parseonetoken()` is a state machine that builds `struct rule` objects, attaches rule code blocks, handles aliases and multiterminals, and stores directive payloads into `struct lemon` or `struct symbol` fields.
5. After parsing, `main()` indexes/sorts symbols, assigns rule numbers with action-bearing rules first, and either reprints grammar (`-g`) or runs the generator pipeline.
6. The generator computes first/lambda sets, LR(0) states, propagation links, follow sets, and actions. `resolve_conflict()` handles shift/shift, shift/reduce, and reduce/reduce conflicts using precedence and associativity where possible.
7. Unless disabled, `CompressTables()` chooses frequent reductions as defaults and converts shifts to auto-reduce states into `SHIFTREDUCE`; `ResortStates()` renumbers states to reduce table size.
8. `ReportOutput()` writes the human-readable automaton report; `ReportTable()` opens `lempar.c`, streams template sections separated by `%%`, injects generated tables and code, and emits the parser C file; `ReportHeader()` writes token defines unless makeheaders mode is active.

## State and Persistence Behavior
- Most generator state is explicit in `struct lemon`, but several module-level static tables persist across one process: `memChunkList`, `x1a` string table, `x2a` symbol table, `x3a` state table, `x4a` config table, configuration/plink/action free lists, option parser globals, and `-D` macro arrays.
- `lemon_free()` only zeroes tracked memory and does not unlink/free individual chunks; bulk cleanup happens through `lemon_free_all()` at process exit.
- `Parse()` loads each grammar file as a single buffer and mutates it in-place while tokenizing. `Strsafe()` interns token strings so the parser can safely release the file buffer after parsing.
- Output persistence is file-based: generated `.c`, `.h`, `.out`, and optional `.sql` names are derived from the grammar filename and `-d` output directory. `ReportHeader()` avoids rewriting an unchanged header.
- `%ifdef` preprocessing comments out excluded regions by replacing non-newline bytes with spaces, preserving line numbering for diagnostics and generated `#line` directives.

## Dependencies and Integration Points
- Depends on the C standard library plus `unistd.h`/`access()` on POSIX or a Windows-compatible `access()` declaration.
- Integrates with `lempar.c` as the parser driver template. `tplt_open()` uses an explicit `-T` template, a grammar-adjacent `.lt` file, local `lempar.c`, or a `PATH`/executable-relative search.
- Generated parsers expose names derived from `%name` or default `Parse`, and support template macros for `%extra_argument`, `%extra_context`, `%token_type`, `%default_type`, `%realloc`, `%free`, stack size, destructors, syntax errors, parse accept/failure, and stack overflow hooks.
- In SQLite builds, Lemon is used by the build system to generate parsers such as SQL grammar output; its generated token header is consumed by scanners unless `-m` delegates header creation to makeheaders.

## Risks and Edge Cases
- `lemon_malloc()` checks `nByte<0` even though `size_t` is unsigned; this is harmless but ineffective for overflow checks. Several allocation-size calculations can still overflow theoretically.
- `lemon_free()` is not a normal free and leaves allocations on `memChunkList`; code expecting immediate reuse or true deallocation would be wrong.
- `Parse()` caps inputs over 100,000,000 bytes but reads the file all at once; extremely large or malformed grammar files still stress memory and scanner paths.
- The scanner handles nested braces and skips C comments/strings, but it is a grammar-specific scanner, not a complete C parser; unusual C constructs in actions can confuse brace matching.
- `ReportTable()` writes SQL text with direct symbol/rule text quoting and is meant for generated diagnostics, not hostile grammar names.
- Conflict resolution depends on symbol order and precedence; unresolved conflicts make process exit fail even if code files were emitted.
- The table compaction and state resort steps affect generated parser table shape, so regression tests should compare behavior rather than relying only on stable table text unless `-r`/`-c` are used.

## Test Signals
- Build `lemon.c`, run it against known SQLite grammar inputs, and verify zero conflicts, generated parser compilation, token header stability, and `.out` reports.
- Exercise option parsing with `-D`, `-U`, `-E`, `-T`, `-d`, `-m`, `-S`, `-c`, and `-r`.
- Use grammars covering precedence resolution, fallback tokens, wildcard tokens, token classes/multiterminals, destructors, default types, extra arguments/context, empty rules, and `NEVER-REDUCE`.
- Verify generated parser behavior through SQLite parser tests, plus `YYCOVERAGE`/`yytestcase` signals in generated parsers.
- Check negative diagnostics: missing start symbol, start symbol on RHS, duplicate labels, unused labels, unterminated strings/C blocks, bad `%if` syntax, and nonterminals with no rules.
