# Research: sources/storage-engines/sqlite/ext/wasm/libcmpp.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008759`: lines 1-7335, `Docs/researches/chunks/subset-b-008759_research.md`
- `subset-b-008760`: lines 7336-16047, `Docs/researches/chunks/subset-b-008760_research.md`
- `subset-b-008761`: lines 16048-16877, `Docs/researches/chunks/subset-b-008761_research.md`

## Chunk Research

### subset-b-008759: lines 1-7335

# sources/storage-engines/sqlite/ext/wasm/libcmpp.c lines 1-7335

## Scope

This chunk covers the beginning of SQLite's vendored `ext/wasm/libcmpp.c` amalgamation through the first line of the `cmpp_undef()` implementation. It includes the generated public `libcmpp` header, the module/plugin ABI surface, the private implementation declarations, the main `cmpp_pimpl` state layout, and the first concrete core implementation routines for construction, reset/destruction, output, delimiters, `@token@` expansion, file slurping, SQL binding helpers, and define lookup. Later directive implementations, database initialization, argument parsing internals, CLI processing, module loading, and the rest of define management continue after this chunk.

## Purpose

- Provide the public API for `libcmpp`, a configurable C-like preprocessor for arbitrary UTF-8 text rather than only C source.
- Package both header and implementation into one amalgamated C file for SQLite's WASM extension tree, with WASM-aware elision of `FILE *` APIs through `cmpp_FILE`.
- Define the central `cmpp` object, its opaque private state, directive context model, token and argument types, output/input abstractions, buffer helpers, policy stacks, delimiter stacks, and module ABI.
- Use SQLite as the backing engine for define storage, include-path tracking, savepoints, token metadata, comparison helpers, and path search queries.
- Support extension points: custom directives, directive autoloaders, loadable modules, and a versioned API thunk for modules which cannot rely on global symbol visibility.
- Begin implementing the core runtime: instance allocation/reset, output channel handling, file slurping, delimiter management, `@token@` expansion, flow-control elision levels, and SQLite statement binding/define lookup helpers.

## Important APIs, Types, And Functions

- Version/configuration macros define the amalgamation provenance: package `libcmpp`, version `2.0.x`, hash `c02f3e3e2d3f3573a9a33c1474c2e52fc48e52c70730404a90d0ae51517e7d37`, timestamp `2026-03-08 14:50:35.123 UTC`, default module path, and platform DLL extension.
- `cmpp_rc_e` is the public result-code enum. It distinguishes ordinary success from OOM, misuse, range, I/O, syntax, DB, undefined-key, assertion, help, no-directive, and unsupported-operation results.
- `cmpp_size_t` and `cmpp_ssize_t` are 32-bit by default via `CMPP_BITNESS`, so string/input sizes and offsets are intentionally bounded to 32-bit ranges unless the library is rebuilt incompatibly with 64-bit counters.
- `cmpp_input_f`, `cmpp_output_f`, and `cmpp_flush_f` are the stream callback contracts. `cmpp_outputer` wraps an output callback, flush callback, cleanup callback, stable state pointer, and optional channel name.
- `cmpp_ctor_cfg` configures a new preprocessor with flags such as no-include, no-pipe, no-db, no-module, and safe mode. It can also name a persistent SQLite database file for defines and runtime state.
- `cmpp_ctor()`, `cmpp_reset()`, and `cmpp_dtor()` allocate the object and private state in one block, initialize policy and delimiter stacks lazily, preserve constructor config across resets, and clean up output, SQL statements, DB handles, directives, modules, buffers, policy stacks, delimiters, and recycled argument state.
- `cmpp_mrealloc()`, `cmpp_malloc()`, and `cmpp_mfree()` are explicit wrappers around SQLite allocation APIs. All buffers returned by this library must be freed with the matching wrapper.
- Define APIs include `cmpp_define_legacy()`, `cmpp_define_v2()`, `cmpp_undef()`, `cmpp_define_shadow()`, and `cmpp_define_unshadow()`. In this chunk the public declarations and lookup helpers are present, and the `cmpp_undef()` implementation begins just after the chunk boundary.
- Processing APIs include `cmpp_process_string()`, `cmpp_process_file()`, `cmpp_process_stream()`, and `cmpp_process_argv()`. Their declarations document the main execution model, CLI flags, include/output behavior, `-D/-U/-F/-I`, inline script execution, delimiter and at-policy options, SQL tracing, and define dumping.
- Error APIs include `cmpp_err_get()`, `cmpp_err_set()`, `cmpp_err_set1()`, `cmpp_err_has()`, and `cmpp_dx_err_set()`. Errors are persistent on the `cmpp` object and most APIs become no-ops while an error is set.
- Savepoint APIs `cmpp_sp_begin()`, `cmpp_sp_commit()`, and `cmpp_sp_rollback()` expose DB transaction nesting for directives; internal declarations add `cmpp__dx_sp_*()` wrappers for directive contexts.
- `cmpp_b` is the owned dynamic byte buffer used for captured output and temporary strings. It tracks `z`, bytes in use, allocation size, and a sticky buffer-local error code.
- `cmpp_tt`, `cmpp_arg`, and `cmpp_args` define directive argument tokenization. Tokens include raw lines, words, integers, strings, at-strings, grouping tokens, comparison operators, arrows, arithmetic operators, boolean operators, glob operators, directives, and EOF.
- `cmpp_d`, `cmpp_d_reg`, `cmpp_dx`, and `cmpp_dx_f` define the directive system. Directives have names, flags, optional closers, callback state, and optional finalizers. `cmpp_dx` owns per-input traversal state and exposes current directive arguments to callbacks.
- Directive flags control raw/list parsing, safe-mode disallowance, call-only behavior, no-call behavior, and internal flow-control/argument simplification semantics.
- `cmpp_dx_next()`, `cmpp_dx_process()`, `cmpp_dx_consume()`, `cmpp_dx_consume_b()`, `cmpp_dx_out_raw()`, and `cmpp_dx_out_expand()` form the directive scanning and block-consumption API used by built-in and custom directive callbacks.
- `cmpp_arg_parse()`, `cmpp_arg_to_b()`, `cmpp_call_str()`, `cmpp_kav_each()`, and `cmpp_str_each()` support token parsing, define expansion, bracket-call expansion, and key/value list traversal for directive implementations.
- Policy APIs `cmpp_atpol_*()` and `cmpp_unpol_*()` manage stacks for undefined `@token@` behavior and undefined define behavior. At policies are off, retain, elide, error, or current; undefined policies are null or error.
- Delimiter APIs `cmpp_delimiter_*()` manage the directive delimiter stack, defaulting to `##`; `cmpp_atdelim_*()` manages paired opening/closing delimiters for `@token@`, defaulting to `@...@`.
- `cmpp_popen()`, `cmpp_popenv()`, `cmpp_pclose()`, and `cmpp_popen_args()` declare Unix child-process integration for directives such as pipe. They are unavailable on WASM and non-Unix builds.
- Module APIs `cmpp_module_load()`, `cmpp_module_dir_add()`, `cmpp_module`, and the `CMPP_MODULE_*` macros define loadable module registration, standalone symbols, and optional dynamic-library discovery.
- `cmpp_api_thunk` and `cmpp_api_thunk_map()` expose a versioned table of public functions and exported objects for loadable modules. The chunk includes generated `CMPP_API_THUNK` macros that rewrite `cmpp_*` calls through the thunk in module builds.
- Internal declarations define `CmppDLine`, `CmppSnippet`, `CmppLvl`, list macros, `CmppArgList`, `cmpp_args_pimpl`, `cmpp_dx_pimpl`, `CmppDList`, `CmppSohList`, `CmppKvp`, POD policy stack macros, `cmpp__delim`, and `cmpp_pimpl`.
- `CmppStmt_map()` enumerates cached SQLite statements for define insertion/deletion/lookup, include tracking, include-path search, comparisons, DB attach/detach, savepoints, token type insertion, and a recursive CTE path search.
- Implemented helpers in this chunk include `cmpp_rc_cstr()`, `cmpp_tt_cstr()`, `cmpp_isspace()`, `cmpp_skip_space()`, `cmpp_skip_snl()`, trailing trim variants, `cmpp_fopen()`, `cmpp_fclose()`, `cmpp_slurp()`, `cmpp_chomp()`, output helpers, delimiter helpers, `cmpp__is_int()`, `cmpp__is_int64()`, `cmpp__set_file()`, `cmpp_has()`, `cmpp__get_bool()`, `cmpp__get_int()`, `cmpp__get_b()`, and `cmpp__get()`.

## Control Flow

The public API starts with `cmpp_ctor()`. It allocates enough memory for both `cmpp` and `cmpp_pimpl`, installs the singleton API thunk pointer, initializes the private state from `cmpp_pimpl_empty`, copies constructor flags and optional database filename, initializes policy stacks, and runs lazy initialization. Lazy initialization pushes the default directive delimiter and `@token@` delimiter levels and optionally calls `CMPP_CTOR_INSTANCE_INIT()` for embedding projects that install custom directives at construction time.

Most public APIs first check `ppCode`, the persistent error code stored in `pp->pimpl->err.code`. If it is nonzero, they return that code or become a no-op. This sticky-error style is intentional: clients can chain calls, and a failure prevents follow-on operations from mutating partially invalid state.

`cmpp_reset()` is the heavy recovery path. It flushes and cleans up SQL trace output, destroys directive autoload state, clears module path bytes, unwinds active savepoints when prepared savepoint statements exist, closes output, frees runtime directive registrations, finalizes prepared statements, commits any open write transaction before closing SQLite, closes the DB handle, clears delimiter stacks, clears errors, and then reinitializes `cmpp_pimpl` while preserving the DB filename, recycler pools, policy storage, delimiter storage, module handle list, allocation stamp, constructor flags, and lazy-init marker.

Output flows through `cmpp_outputer` callbacks. `cmpp_outputer_set()` replaces the default channel, `cmpp__out_fopen()` opens a FILE-backed channel, `cmpp__out_close()` flushes and calls cleanup, `cmpp__out2()` writes bytes and records write errors, and `cmpp_dx_out_raw()` suppresses output when the current directive context is in elide mode. Formatted output uses SQLite's `sqlite3_vmprintf()` before writing.

`cmpp__out_expand()` is the key implemented filter in this chunk. It walks a byte range looking for the current at-token opening delimiter. Raw spans before tokens are flushed to the selected output. A `@[directive ...]@` form is treated as an inline call: the bracket content is located with `cmpp__find_closing2()`, processed via `cmpp_call_str()`, and emitted. A normal token extracts the key between opening and closing delimiters, looks up the define with `cmpp__get_b()`, emits the value when found, and otherwise applies the active policy: elide, retain, or error. It borrows temporary buffers from the `cmpp` buffer recycler and returns them before exit.

Delimiter control is stack based. `cmpp_delimiter_push()` appends a delimiter slot, then delegates to `cmpp_delimiter_set()`. On failure, it pops the newly added slot. `cmpp_delimiter_pop()` restores the previous delimiter by cleaning up the top slot. The at-token delimiter APIs do the same, except `cmpp_atdelim_set()` stores opening and closing delimiters in a single owned buffer.

Flow-control elision is represented by `CmppLvl` entries in `cmpp_dx_pimpl::dxLvl`. `CmppLvl_push()` inherits the parent elide bit and records the directive line number. `cmpp_dx_is_eliding()` reads the top level, and output functions use it to suppress text from falsy branches.

Define lookup uses cached SQLite statements. `cmpp_has()` binds a key and checks for a row in `vdef`. `cmpp__get_bool()` reads `cmpp_truthy(v)`, `cmpp__get_int()` casts the selected value to integer, `cmpp__get_b()` appends the value to a `cmpp_b`, and `cmpp__get()` returns a newly allocated copy. Missing entries optionally enforce the undefined-key policy through `cmpp__affirm_undef_policy()`.

File input in this chunk is eager rather than streaming. `cmpp_slurp()` repeatedly calls a `cmpp_input_f`, reallocates a destination buffer, copies all bytes, and NUL-terminates the result. `FileWrapper` builds on that for named files and underlies `cmpp__set_file()`, the implementation helper for `-Fkey=file`, which reads file content, optionally chomps one trailing newline, and inserts the bytes into the define table.

## State And Persistence Behavior

`cmpp_pimpl` is the core mutable state. It owns the SQLite handle and optional database filename, current directive context pointer, output channel, directive and at-token delimiter stacks, cached SQLite statements, sticky error state, SQL trace channel, constructor/runtime flags, policy stacks, runtime directive list and autoloader, module/shared-object state, and recycler pools for buffers and argument pimpls.

Defines, shadow defines, include records, include paths, token metadata, and some lookup/comparison behavior are persisted in SQLite tables or views managed by later database-initialization code. This chunk shows the statement map and the lookup/binding side of that design. If `cmpp_ctor_cfg::dbFile` is non-null, that SQLite state can be backed by a named database file; otherwise the implementation uses an unspecified temporary or in-memory DB once initialized.

Persistent error state gates almost every operation. The code treats most errors as unrecoverable without `cmpp_reset()`, because a mid-processing failure can leave savepoints, directives, or output state imbalanced. Some API docs call specific errors recoverable, but the dominant runtime model is fail-stop until reset.

The output channel is owned or borrowed depending on the `cmpp_outputer` supplied by the caller. `cmpp_outputer_set()` bitwise-copies callback state and later cleanup may close or mutate the copied outputer's `state`, so ownership rules are part of the caller contract.

Delimiter and policy state is stack-based. Push operations allocate or reserve state and require a matching pop on success. `cmpp_reset()` clears active delimiter entries but keeps the underlying delimiter-list storage for reuse, then marks the object for lazy reinitialization.

Module state includes a DLL/shared-object handle list and module search path. This chunk sets up cleanup rules and state but leaves actual module loading to later code. The comments intentionally note that DLLs are normally unsafe to close, but this build defaults `CMPP_CLOSE_DLLS` to true for valgrind-style cleanup.

Buffer and argument recyclers are retained across reset and cleaned only in `cmpp_dtor()`. That improves reuse during repeated processing but means a reset is not a full memory release.

## Dependencies And Integration Points

- SQLite is the central dependency: allocation (`sqlite3_malloc64`, `sqlite3_realloc64`, `sqlite3_free`), formatting (`sqlite3_mprintf`, `sqlite3_vmprintf`, `sqlite3_str`), database handles, prepared statements, bindings, savepoints, transactions, CTE path search, and runtime scalar functions such as `cmpp_truthy`, `cmpp_compare`, and `cmpp_file_exists`.
- Platform I/O integrates with `stdio.h`, `unistd.h`, `sys/wait.h`, or Windows `_access`/I/O headers depending on build macros. WASM builds typedef `cmpp_FILE` to `void` and mark many file/process APIs unavailable or inoperative.
- SQLite's WASM extension tree consumes this file as a vendored amalgamation under `ext/wasm`; the header also points to SQLite's lighter `c-pp-lite.c` as a related deployment.
- Loadable modules integrate through `cmpp_module_init_f`, `cmpp_d_register()`, `CMPP_MODULE_*` registration macros, dynamic-library search path state, and `cmpp_api_thunk`.
- Custom directives integrate through `cmpp_d_register()`, directive flags, `cmpp_dx_f` callbacks, `cmpp_dx` traversal/output/argument APIs, and directive autoloaders.
- The CLI integration is declared through `cmpp_process_argv()` and usage output. This connects public options such as `-D`, `-U`, `-F`, `-I`, `-e`, `--delimiter`, `--@policy`, SQL tracing, and define dumping to the library runtime.
- External process integration is declared through `cmpp_popen*()` and is intended for directives such as pipe. Safe mode and constructor flags can disable unsafe filesystem/process/module behaviors.

## Risks And Edge Cases

- The chunk is an amalgamation. Public header, private declarations, generated thunk macros, and implementation coexist in one file, so symbol visibility and macro state are unusually sensitive to compile-time defines.
- Many APIs become silent no-ops when persistent error state is set. This simplifies call chains but can hide the exact operation that stopped doing work unless callers check `cmpp_err_get()`.
- `cmpp_reset()` is intentionally broad and closes the database, removes custom directives/autoloaders, clears paths, finalizes statements, and resets delimiters. Clients expecting partial recovery must preserve and reinstall custom state.
- Output ownership is easy to misuse because outputers are bitwise copied. A cleanup callback may close a state pointer that the caller still considers live unless the caller follows the documented copy-with-null-cleanup pattern.
- `cmpp_slurp()` reallocates by assigning directly to `pDest`; if `cmpp_mrealloc()` returns NULL, the old pointer is lost and the subsequent `memcpy()` would be unsafe. The code does not check allocation failure inside the loop before copying.
- `cmpp_slurp()` uses `unsigned` counters for allocation and offsets even though the public size type is `cmpp_size_t`; very large inputs can overflow these local counters in 32-bit builds.
- `cmpp_skip_snl_trailing()` tests `*z` while moving backward from a one-past-end pointer, which is suspicious relative to `cmpp_skip_space_trailing()` using `z[-1]`; the comment already calls out CRNL handling as incomplete.
- `cmpp__out_expand()` deliberately does not error on an unterminated at-token at EOF because the error block is compiled out. That can retain or flush partially parsed token text rather than reporting syntax failure.
- The at-token call path around `@[...]@` has subtle pointer math involving delimiter lengths and bracket positions; delimiter lengths greater than one increase the need for tests.
- `cmpp__out_expand()` borrows two buffers and immediately returns on the second borrow failing without returning the first buffer if only the second allocation failed.
- `cmpp__set_file()` appears to bind NULL to column 2 in the empty-file branch after binding the key to column 2 earlier; for `defIns(t,k,v)` this is likely a key/value column mix-up unless later code compensates before the chunk boundary.
- `cmpp__is_int()` and `cmpp__is_int64()` rely on `sscanf()` with width macros and do not prove that the full token is numeric; prefixes may parse as integers if not validated elsewhere.
- Safe mode depends on directive registration and processing honoring `cmpp_d_F_NOT_IN_SAFEMODE`. Client-defined directives must set that flag correctly for filesystem, network, process, and similar effects.
- WASM builds define `cmpp_FILE` as `void`, but the comments admit FILE dependencies are not fully compiled out. Any accidental use of `FILE`-oriented APIs in WASM builds can become unsupported or inoperative.
- `cmpp_dtor()` only frees the outer allocation if `allocStamp` matches the canonical empty pimpl marker. Stack/static or manually embedded instances would need compatible initialization discipline.

## Test Signals

- Constructor/destructor tests should cover default construction, construction with `dbFile`, safe-mode flags, lazy delimiter/policy initialization, repeated `cmpp_reset()`, and final `cmpp_dtor()` cleanup.
- Error-state tests should set an error, verify subsequent APIs no-op, verify `cmpp_reset()` is needed for full recovery, and verify `cmpp_check_oom()` behavior with both NULL and non-NULL `cmpp`.
- Output tests should cover no-op outputers, FILE outputers including `"-"` for stdin/stdout selection, buffer outputers, flush failures, cleanup ownership patterns, formatted output, and elide-mode suppression.
- Slurp/file tests should cover empty input, large input, read errors, allocation failure injection, `cmpp_chomp()` for LF and CRLF, `-Fkey=file` behavior, and empty-file define insertion.
- Delimiter tests should cover default directive delimiter, custom delimiter, too-long delimiter, empty/control-character delimiters, push/pop balance, popping an empty stack, and multi-character at-token open/close pairs.
- At-token expansion tests should cover policies off/retain/elide/error, defined and undefined keys, empty keys, custom delimiters, tokens spanning line boundaries, unterminated tokens, and `@[directive ...]@` call expansion.
- Policy-stack tests should cover push/pop balancing for at policies and undefined-key policies and confirm undefined-key error policy affects `cmpp__get_bool()`, `cmpp__get_int()`, `cmpp__get_b()`, and `cmpp__get()`.
- SQLite-backed define tests should cover define existence, truthiness, integer extraction, NULL/empty values, shadow precedence via `vdef`, glob deletes once `cmpp_undef()` implementation is included, and statement reset after each lookup.
- Flow-control tests should confirm nested `CmppLvl` inheritance, elision toggling, and suppression of raw and expanded output in inactive `#if` branches.
- Module/thunk tests should compile a small directive module with `CMPP_API_THUNK`, verify API version compatibility, register directives through `cmpp_api_init()`, and ensure module path defaults and explicit directory additions behave when module support is enabled or omitted.
- WASM configuration tests should build with WASM macros and verify unsupported FILE/process/module paths report `CMPP_RC_UNSUPPORTED` or no-op consistently without depending on Emscripten POSIX I/O proxies.

### subset-b-008760: lines 7336-16047

# sources/storage-engines/sqlite/ext/wasm/libcmpp.c lines 7336-16047

## Scope

This chunk covers a large middle section of the amalgamated `libcmpp.c` source. It spans public and internal setup helpers, directive tokenization and dispatch, the SQLite-backed define/include database, built-in directive implementations, argument parsing and expression evaluation, process piping, dynamic module loading, and the opening of SQLite's embedded `generate_series` virtual table implementation. The chunk begins in the tail of define/include-path management and ends after the `seriesColumn()` implementation and integer limit macros for `generate_series`; later virtual-table methods continue beyond this range.

## Purpose

The code in this range is the operational core of the `cmpp` preprocessor. It turns an input string/file/stream into output by scanning for directive delimiters at line starts, parsing directive arguments, resolving or lazily registering directive handlers, executing built-in directives, and maintaining define/include/module state in an internal SQLite database. It also exposes utility APIs used by embedders: output/input callbacks, policy getters/setters, savepoint control, CLI argument processing, buffer recycling, SQL query binding, subprocess piping, and dynamic module loading.

## Important APIs, Types, and Functions

- Include/module/db setup:
  - `cmpp__include_dir_add()`, `cmpp_include_dir_add()`, `cmpp__include_dir_rm_id()` maintain rows in the internal `inclpath` table and update `nIncludeDir`.
  - `cmpp_module_dir_add()` appends module search-path entries, normalizing `CMPP_PATH_SEPARATOR` into the configured module path separator when DLL support is enabled.
  - `cmpp_db_name_set()` selects a persistent SQLite database filename before `cmpp__db_init()` opens the database.
  - `cmpp_path_search()` delegates module/file path lookup to a prepared SQLite statement.

- Directive scanning and processing:
  - `cmpp_next_chunk()`, `cmpp__dx_next_line()`, and `cmpp_dx_delim_search()` scan input, track source line numbers, flush non-directive text, identify directive lines, and handle grouped constructs and escaped newlines.
  - `cmpp_dx_next()` normalizes a directive line, resolves the directive with `cmpp__d_search3()`, validates call-only/no-call flags, and parses raw or list arguments according to directive flags.
  - `cmpp_dx_process()` invokes the directive callback unless the current conditional level is eliding and the directive is not flow-control.
  - `cmpp_dx_consume()` and `cmpp_dx_consume_b()` consume nested directive bodies up to configured closers and optionally process intervening directives.

- Directive registration:
  - `cmpp_d_register()` registers opener and optional closer directive entries in a sorted `CmppDList`, checks safe-mode restrictions, validates directive names, and associates callback state/destructors.
  - `cmpp__d_delayed_load()` lazily registers built-in directives such as `if`, `define`, `include`, `query`, `pipe`, `module`, `delimiter`, `@`, `arg`, `join`, `file`, and policy/debug helpers.
  - `CmppDList_*` helpers own directive-entry allocation, cleanup, sorting, and lookup.

- Policy and savepoint APIs:
  - `cmpp_atpol_*` and `cmpp_unpol_*` map string names to policy enums, expose get/set, and support scoped push/pop stacks via generated POD list helpers.
  - `cmpp_sp_begin()`, `cmpp_sp_rollback()`, `cmpp_sp_commit()` wrap SQLite savepoints; `cmpp__dx_sp_*()` mirror them with per-input-source tracking so script-level savepoints are cleaned up during directive context teardown.

- Processing entry points:
  - `cmpp_process_string()`, `cmpp_process_file()`, and `cmpp_process_stream()` initialize the database, set up a `cmpp_dx`, shadow `__FILE__`, manage input-local include path priority, repeatedly call `cmpp_dx_next()`/`cmpp_dx_process()`, and flush output.
  - `cmpp_call_str()` runs a directive in call context, optionally prepends the current directive delimiter, captures output into a buffer, and applies trimming flags.
  - `cmpp_process_argv()` implements the historical CLI driver for `-D`, `-U`, `-I`, `-L`, `-F`, `-e`, `-o`, delimiter/policy/debug/db flags, SQL tracing, and file processing.

- Buffer, output, and stream helpers:
  - `cmpp_b_*` implements an appendable NUL-terminated byte buffer plus a `cmpp`-owned recycler via `cmpp_b_borrow()` and `cmpp_b_return()`.
  - `cmpp_outputer_*`, `cmpp_stream()`, `cmpp_input_f_FILE()`, `cmpp_output_f_FILE()`, `cmpp_input_f_fd()`, and `cmpp_output_f_fd()` form generic I/O adapters.
  - Optional `cmpp__obuf` support wraps buffered output behind a `cmpp_outputer`.

- SQLite database layer:
  - `cmpp__prepare()`, `cmpp__stmt()`, `cmpp__step()`, `cmpp__stmt_reset()`, `cmpp__db_rc()`, and `cmpp__db_errcode()` centralize prepared statement creation, stepping, reset, and error mapping.
  - `cmpp__db_init()` opens `:memory:` or a configured DB file, installs tracing, registers UDFs, creates the schema, initializes SQLite's `series` module, prepares savepoint statements, and performs lazy initialization.
  - `cmpp__define_impl()`, `cmpp__define2()`, `cmpp__define_legacy()`, `cmpp_define_v2()`, `cmpp_define_shadow()`, and `cmpp_define_unshadow()` populate either persistent defines (`def`) or scoped shadow defines (`sdef`).
  - `cmpp__define_from_row()` maps query result columns to defines using SQLite column names and type mapping.

- Built-in directives:
  - `cmpp_dx_f_define()` supports scalar define, grouped `key -> value` define lists, expression/call-derived values, `?` define-if-absent mode, `-append`, heredoc `<<`/`<<<`, and chomp handling.
  - `cmpp_dx_f_undef()`, `cmpp_dx_f_error()`, `cmpp_dx_f_expr()`, `cmpp_dx_f_once()`, `cmpp_dx_f_if()`, `cmpp_dx_f_if_dangler()`, `cmpp_dx_f_pragma()`, `cmpp_dx_f_savepoint()`, `cmpp_dx_f_stderr()`, `cmpp_dx_f_at()`, `cmpp_dx_f_undef_policy()`, and `cmpp_dx_f_delimiter()` implement core preprocessing behavior.
  - Optional unsafe directives include `cmpp_dx_f_include()`, `cmpp_dx_f_pipe()`, `cmpp_dx_f_attach()`, `cmpp_dx_f_detach()`, `cmpp_dx_f_query()`, `cmpp_dx_f_file()`, and `cmpp_dx_f_module()`, guarded by compile-time flags, constructor flags, and safe mode.
  - Utility directives `sum`, `arg`, `join`, and `cmp` expand arguments and emit calculated text.

- Argument parsing and evaluation:
  - `cmpp_args__init()`, `cmpp_args_parse()`, `cmpp_arg_parse()`, `cmpp_args_clone()`, and `cmpp_dx_args_parse()` allocate/reuse parser state and tokenize directive arguments into `cmpp_arg` lists.
  - `cmpp_tt_forWord()` maps symbolic tokens such as `==`, `!=`, `<`, `<=`, `glob`, `not`, `defined`, `->`, `<<`, and `<<<` to token types.
  - `cmpp__args_evalToInt()`, `cmpp__arg_toBool()`, comparison operator helpers, and `cmpp_args__not_simplify()` implement expression evaluation over integers, defines, string truthiness, glob matching, nested groups, calls, and comparison SQL statements.
  - `cmpp_arg_to_b()`, `cmpp__bind_arg()`, `cmpp_kav_each()`, `cmpp_str_each()`, and `cmpp__arg_expand_ats()` convert arguments into output bytes, SQL bind values, or key/value callback inputs.

- External integration:
  - `cmpp_popen()`, `cmpp_popenv()`, `cmpp_popen_args()`, and `cmpp_pclose()` provide Unix process execution used by `#pipe`.
  - DLL helpers `cmpp__dlopen()`, `cmpp__dlsym()`, `cmpp__dlclose()`, `cmpp__module_extract()`, and `cmpp_module_load()` load `cmpp_module` entry points from shared libraries when compiled with DLL support.
  - The chunk begins the embedded `generate_series` virtual table: `series_cursor`, `span64()`, `add64()`, `sub64()`, `seriesConnect()`, `seriesDisconnect()`, `seriesOpen()`, `seriesClose()`, `seriesNext()`, and `seriesColumn()`.

## Control Flow

Input processing starts at `cmpp_process_string()`, which initializes SQLite state, creates a stack-local `cmpp_dx`, shadows `__FILE__`, adds the source directory to the include path with a priority based on nesting depth, then loops over `cmpp_dx_next()` until no directive remains. `cmpp_dx_delim_search()` emits ordinary text as it scans and stops only when the current delimiter is found at beginning-of-line after optional spaces. Once a directive line is identified, `cmpp_dx_next()` normalizes escaped newlines, splits the directive name from the argument text, resolves or lazily registers the directive, and creates either parsed argument lists or a raw-line argument. `cmpp_dx_process()` then calls the directive implementation.

Nested/body directives use `cmpp_dx_consume()`. It repeatedly calls `cmpp_dx_next()` until it sees one of the expected closer directives. Depending on flags, it either rejects intervening directives or processes them. This mechanism is used by heredoc-like `#define`, `#once`, `#if`, `#query`, `#pipe`, delimiter/policy scoped blocks, and dangling-closer diagnostics.

The conditional flow in `cmpp_dx_f_if()` creates a `CmppLvl` stack entry, evaluates the initial expression unless already eliding, and then consumes until `elif`, `else`, or `/if` while toggling the level's elide flag. It deliberately processes nested flow-control directives even in skip mode so nesting stays balanced.

SQL-backed directives follow a separate flow. `#query` clones the directive arguments, resolves SQL and optional bind groups, optionally starts a savepoint, steps rows, defines each result column into the current define view, replays the directive body for each row by restoring `cmpp_dx_pos`, and consumes a `query:no-rows` body if no row matched. `#attach`/`#detach` bind schema/database names into prepared statements.

The CLI driver intentionally walks arguments twice: first for validation/help/version handling and then for execution. This lets flags and files be interleaved, so define/output/include/module state changes affect later file processing in command-line order.

## State and Persistence Behavior

Most preprocessor state is anchored in `cmpp_pimpl`: current error, outputer, directive registry, delimiter and policy stacks, module path/handles, SQLite handles/statements, buffer recyclers, and the active `cmpp_dx`. The input-local `cmpp_dx_pimpl` tracks source span, position/line number, current directive line, parsed args, nested levels, savepoint count, and shadow rows for source-local state.

Defines and include state are persisted in SQLite tables:

- `def` stores ordinary user defines.
- `predef` stores built-ins such as `cmpp::version`.
- `sdef` stores scoped/shadow defines such as per-source `__FILE__`.
- `vdef` merges predefined, scoped, and ordinary defines with ordering that makes predefined and latest scoped values take precedence.
- `incl` tracks files currently being included for recursion detection.
- `inclpath` stores include search paths with priority.
- `modpath` is declared in schema but this chunk primarily uses `pp->pimpl->mod.path` plus `cmpp_path_search()` for module lookup.

`cmpp_db_name_set()` can make the SQLite database file-backed, but `cmpp__db_init()` drops and recreates the cmpp schema for persistent files, so the file is a persistence medium for a run rather than a schema migration target. Savepoints are real SQLite savepoints and are forcibly rolled back during `cmpp_dx_cleanup()` if a directive context exits with active script-local savepoints.

Memory ownership is explicit and mostly local. Directive entries own copied names and optional callback state destructors. `cmpp_b` and `cmpp_args_pimpl` instances are recycled through `cmpp_pimpl->recycler` to reduce allocations. Dynamic module handles may be tracked in `CmppSohList` when closing is enabled; otherwise handles are intentionally left open.

## Dependencies and Integration Points

The chunk depends heavily on SQLite's C API: prepared statements, views, UDF registration, tracing, dynamic SQL strings, `sqlite3_strglob()`, `sqlite3_mprintf()`, virtual table APIs, and the `generate_series` extension initializer. It also uses standard/POSIX APIs including `fopen`/`fread`/`fwrite`, `read`/`write`, `access`, `stat`, `pipe`, `fork`, `dup`, `exec*`, `fdopen`, `waitpid`, signals, and dynamic loader APIs (`dlopen`/`dlsym`/`dlclose` or libltdl).

The public exported surface in this chunk is suitable for embedders: callers can configure policies, process strings/files/streams, register directives, define/undefine keys, set output callbacks, run call-form directives, load modules, inspect/take errors, and manage savepoints. Compile-time flags such as `CMPP_OMIT_D_DB`, `CMPP_OMIT_D_INCLUDE`, `CMPP_OMIT_D_PIPE`, `CMPP_ENABLE_DLLS`, `CMPP_D_MODULE`, `CMPP_MAIN`, and platform macros substantially alter available behavior.

Safe mode is enforced in two places: directive registration rejects `cmpp_d_F_NOT_IN_SAFEMODE` directives, and `cmpp_dx_process()` checks the flag before callback invocation. Unsafe built-ins are also marked or constructor-flag gated. Module loading has its own safe-mode check.

## Risks and Edge Cases

- `cmpp_dx_delim_search()` only recognizes directives at beginning-of-line after optional spaces. Its line-number and flush logic is subtle because it must not prematurely emit indentation before a directive and must handle blank lines, CRLF, escaped newlines, and grouped delimiters.
- `cmpp__find_closing2()` only validates a top-level group. The comment explicitly notes that malformed inner groups may be deferred to argument parsing.
- Many APIs are gated by `ppCode`/`dxppCode`; savepoint rollback and statement preparation sometimes intentionally work during an error state. Misusing that convention can leave statements unprepared or cleanup paths unable to recover.
- `cmpp_b_reserve()` grows by `s->nAlloc + n`, where callers often pass required total size. This overallocates but preserves amortized safety; callers rely on NUL termination after appends.
- `cmpp_b_borrow()` asserts that returned buffers are not written after return. Violations are debug-time only and could cause hard-to-find memory aliasing in release builds.
- Directive list lookup uses binary search only when more than two entries exist, so `CmppDList_sort()` after registration is required. Missing a sort would make delayed directives intermittently unfindable.
- `cmpp_dx_f_cmp()` contains `if( !bL || !!bR ) goto end;`, which appears suspicious because it exits when `bR` is non-NULL rather than when it is NULL. That likely makes `#cmp` a no-op/error-prone path unless masked elsewhere.
- `#query` always rolls back the savepoint it starts when not in `define` mode. This appears intentional so row-defined variables are scoped to each row body, but changes made inside query bodies may also be rolled back depending on directive behavior.
- `#pipe` writes the full captured body to child stdin before reading stdout and the inline comment notes this can deadlock for large bodies.
- `cmpp_pclose()` uses `waitpid(..., WNOHANG)` in a loop that only iterates while `wp > 0`; it may return before a still-running child exits, potentially leaving cleanup behavior dependent on later process reaping.
- Dynamic module search constructs names and loads DLLs from configured paths. Safe mode blocks this, but non-safe builds must consider search-path injection and module lifetime.
- `cmpp__udf_compare()` uses `strncmp()` with the larger byte length of two SQLite text values; this is not a raw `memcmp()` and may read until a NUL within strings. It is adequate for NUL-terminated SQLite text but not a general blob comparator despite accepting text/blob types.
- `cmpp_arg_parse()` does not implement backslash escaping in quoted strings; users must choose the alternate quote character or group syntax for embedded quotes.
- `cmpp_args__not_simplify()` comments that eliminating `not` operators may change coercion behavior from forced boolean conversion to whatever the LHS consumer wants.
- File path handling has explicit TODOs around canonicalization, Windows support, include path normalization, and `getcwd()` behavior. Different spellings of the same include path/file can bypass recursion or uniqueness expectations.
- The `generate_series` virtual table implementation has signed/unsigned integer aliasing helpers (`span64`, `add64`, `sub64`) that rely on reinterpretation through pointer casts; this mirrors upstream SQLite extension style but is sensitive to strict-aliasing/compiler assumptions.

## Test Signals

Useful tests for this chunk should cover:

- Directive delimiter scanning with leading spaces, blank lines, CRLF, escaped newlines, grouped `{}`, `[]`, `()`, and no-directive passthrough output.
- Lazy registration and unknown directive errors, including call-only/no-call directives and safe-mode blocked directives.
- `#define` scalar, grouped `key -> value`, `?`, `-append`, heredoc, chomp, expression, and call-brace forms; `#undef` glob/key removal; `#once` duplicate suppression keyed by `__FILE__` and line number.
- `#if`/`#elif`/`#else`/`#/if` nesting, elided branches containing unknown or delayed directives, and unterminated nested construct diagnostics.
- `@` token policy and delimiter push/pop/set/heredoc behavior, including empty-stack pop errors and call-form introspection.
- Savepoint begin/commit/rollback at both public API and directive level, including cleanup rollback after errors.
- Include path priority for nested files, recursive include detection, raw include streaming, and missing file errors.
- SQL database initialization, persistent DB reset behavior, UDFs (`cmpp_file_exists`, `cmpp_truthy`, `cmpp_compare`), SQL tracing, `#attach`/`#detach`, `#query` bind groups, batch mode, define mode, row body replay, and `query:no-rows`.
- CLI order-dependent processing with interleaved `-D`, `-U`, `-I`, `-L`, `-o`, `-e`, file inputs, policies, and SQL trace flags.
- Argument parser coverage for quote strings, `@"..."`, groups, heredoc tokens, operators, `defined`, `glob`, path-like words, nested expression evaluation, boolean coercion, and key/value iteration.
- `#pipe` with no input, captured body input, `--` command form, `[...]` argv form, chomp flags, direct/path execution, stderr behavior, large-input deadlock risk, and safe-mode blocking.
- Module loading success/failure paths, symbol-name variants, module init errors, missing DLLs, search-path behavior, and safe-mode rejection.
- Embedded `generate_series` queries through the initialized SQLite connection once the rest of the virtual-table implementation is included by the final merge chunk.

## Cross-Chunk Notes

This chunk starts immediately after preceding define/undefine logic and therefore assumes earlier declarations for macros, structs, prepared-statement maps, output helpers, define lookup helpers, delimiter helpers, and low-level SQLite bind helpers. It ends in the middle of the SQLite `generate_series` extension. The final per-file reconciliation should merge this with later chunks to describe the remaining virtual-table methods (`xRowid`, `xEof`, `xFilter`, `xBestIndex`, registration entry point, etc.) and with earlier chunks for constructors, schema statement maps, delimiter stack primitives, and output expansion internals.

### subset-b-008761: lines 16048-16877

# sources/storage-engines/sqlite/ext/wasm/libcmpp.c lines 16048-16877

## Scope

This chunk covers the tail of SQLite's `generate_series` virtual-table extension embedded in `libcmpp.c`, followed by the beginning of the c-pp demonstration directive module. The `generate_series` portion includes cursor rowid/EOF helpers, 64-bit step-count and floating bound helpers, `seriesFilter()`, `seriesBestIndex()`, the `sqlite3_module` method table, and `sqlite3_series_init()`. The c-pp portion defines demo directive callbacks, HTML div wrapper helpers, directive autoloading, and `cmpp_module__demo_register()`.

## Purpose

- Implement the scan-time and planner-time logic for SQLite's `generate_series` virtual table.
- Translate hidden-column constraints, `value` constraints, ordering, `LIMIT`, and `OFFSET` into a bounded integer cursor range without signed-overflow undefined behavior.
- Register the `generate_series` virtual table with SQLite when virtual tables are enabled.
- Provide sample c-pp directives that demonstrate argument handling, paired open/close directives, block consumption, autoload registration, per-directive state, and module registration.

## Important APIs, Types, And Functions

- `seriesRowid()` returns the current generated integer as the SQLite rowid.
- `seriesEof()` reports `series_cursor.bDone`, which is set by `seriesFilter()` for empty scans and by `seriesNext()` after the terminal value is emitted.
- `seriesSteps()` computes how many increments separate `iBase` and `iTerm` using `span64()` and unsigned `iStep`, honoring ascending and descending scans.
- `seriesCeil()` and `seriesFloor()` abstract ceil/floor behavior. They use libc math when available, compiler builtins on GCC/Clang when allowed, and local integer-based fallbacks otherwise.
- `seriesFilter()` is the virtual-table `xFilter` implementation. It consumes the `idxNum` bitmask and SQLite values prepared by `seriesBestIndex()`, initializes `series_cursor`, narrows the range, applies ordering, and applies `LIMIT`/`OFFSET`.
- `seriesBestIndex()` is the virtual-table planner hook. It inspects `sqlite3_index_info` constraints, builds the `idxNum` bitmask, assigns argument indexes, marks constraints omittable when safe, estimates cost/rows, consumes compatible `ORDER BY`, and rejects unusable input constraints.
- `seriesModule` wires the virtual-table method table, using `seriesConnect`, `seriesDisconnect`, `seriesOpen`, `seriesClose`, `seriesFilter`, `seriesNext`, `seriesEof`, `seriesColumn`, and `seriesRowid`.
- `sqlite3_series_init()` is the extension entry point. It checks the SQLite version for older runtimes and calls `sqlite3_create_module(db, "generate_series", &seriesModule, 0)`.
- `cmpp_dx_f_demo1()` is a simple c-pp directive callback that emits a greeting and dumps each parsed argument's token type, length, and text.
- `divOpener()` emits an opening HTML `<div>` tag, treating directive arguments as CSS class names.
- `cmpp_dx_f_divOpen()` and `cmpp_dx_f_divClose()` implement a paired directive with stateful nesting count.
- `cmpp_dx_f_divWrapper()` consumes input until the matching closer directive, processes nested directives, chomps trailing whitespace, and wraps the captured content in a div.
- `cmpp_d_autoload_f_demos()` lazily registers demo directives by name, including closer-name aliases where appropriate.
- `cmpp_module__demo_register()` eagerly registers the demo directives with a c-pp instance.

## Control Flow

For `generate_series`, planning starts in `seriesBestIndex()`. It scans `pIdxInfo->aConstraint` and recognizes equality constraints on hidden `start`, `stop`, and `step` columns; equality and range constraints on `value` or rowid; `LIMIT`; and `OFFSET`. It records the selected constraints in `aIdx[]`, sets matching bits in `idxNum`, and assigns `argvIndex` values in the exact order expected by `seriesFilter()`: start, stop, step, limit, offset, lower/equality value constraint, then upper value constraint. Without `ZERO_ARGUMENT_GENERATE_SERIES`, the planner requires either a usable `start=` constraint or a usable value/rowid lower/equality constraint and returns an error message if the first argument is missing or unusable.

At scan time, `seriesFilter()` first rejects any NULL constraint value by jumping to the no-rows path. It loads original `start`, `stop`, and `step` values into `iOBase`, `iOTerm`, and `iOStep`, using defaults of `0`, `0xffffffff`, and `1` for omitted inputs. If only `value` constraints are present, the default generation range is widened to the full signed 64-bit range so the value constraints can define the effective bounds.

`seriesFilter()` stores the absolute step magnitude in unsigned `iStep`, including the `SMALLEST_INT64` negative-step case that requires a magnitude of `9223372036854775808`. It rejects directionally impossible ranges before processing output-value constraints. Equality, lower-bound, and upper-bound constraints on `value` are converted into integer `iMin` and `iMax` bounds, with floating-point inputs accepted only when they can be rounded according to SQL comparison semantics without falling outside signed 64-bit range. The cursor range is then advanced or contracted to the first reachable value within those bounds.

After value-constraint narrowing, `seriesFilter()` snaps `iTerm` to the last value actually reachable from `iBase` by a whole number of steps. If the planner consumed an `ORDER BY` request that is opposite to the natural step direction, it swaps `iBase` and `iTerm` and flips `bDesc`. Finally, it applies `OFFSET` by advancing `iBase` and applies non-negative `LIMIT` by shortening `iTerm`. Success initializes `iValue = iBase` and clears `bDone`; all empty or invalid cases reset the cursor to a benign one-row-shape state with `bDone = 1`.

The module table exposes the generate-series cursor as a read-only, innocuous virtual table. `sqlite3_series_init()` installs that module unless virtual tables are omitted.

The c-pp demo module starts with build-mode preprocessor selection: when compiled as part of the main c-pp app, `CMPP_D_DEMO` keeps the code inline; when built as a standalone module and the module-registration helper is absent, it defines `CMPP_MODULE_STANDALONE`/`CMPP_API_THUNK` and includes `libcmpp.h`. Directive execution then flows through callbacks registered by `cmpp_d_autoload_f_demos()` or `cmpp_module__demo_register()`. The wrapper directive calls `cmpp_dx_consume_b()` with its closer descriptor and `cmpp_dx_consume_F_PROCESS_OTHER_D`, so nested directives are processed while the block is consumed.

## State And Persistence Behavior

The `generate_series` implementation has no persistent storage of its own. Its state is a transient `series_cursor` allocated by `seriesOpen()` and freed by `seriesClose()`. The cursor preserves original hidden-column inputs for `seriesColumn()` output while separately tracking the optimized generation range in `iBase`, `iTerm`, `iStep`, `iValue`, `bDesc`, and `bDone`. `seriesBestIndex()` only mutates the transient `sqlite3_index_info` plan object and, on missing required input, `pVTab->zErrMsg`.

The c-pp demo directives also do not write durable state. `demo-div` allocates an `int` counter as directive state through `cmpp_malloc()` and registers `cmpp_mfree` as its destructor. That counter tracks currently open `demo-div` blocks for the registered directive instance. `cmpp_dx_f_divWrapper()` owns a temporary `cmpp_b` buffer for consumed content and always clears it before returning.

Output effects are immediate: the demo callbacks write to the c-pp output stream through `cmpp_dx_outf()` and `cmpp_dx_out_raw()`, and errors are stored in the processor/directive execution context through `cmpp_dx_err_set()` or the broader `cmpp_err_get()` path.

## Dependencies And Integration Points

- SQLite virtual table APIs: `sqlite3_vtab_cursor`, `sqlite3_index_info`, `sqlite3_module`, `sqlite3_declare_vtab()`, `sqlite3_create_module()`, constraint op constants, `sqlite3_value_*()`, `sqlite3_result_int64()`, `sqlite3_malloc()`, `sqlite3_free()`, and `sqlite3_mprintf()`.
- Earlier `generate_series` helpers and types in the same file: `series_cursor`, `span64()`, `add64()`, `sub64()`, `seriesConnect()`, `seriesDisconnect()`, `seriesOpen()`, `seriesClose()`, `seriesNext()`, and `seriesColumn()`.
- Compile-time gates: `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_SERIES_CONSTRAINT_VERIFY`, `ZERO_ARGUMENT_GENERATE_SERIES`, `SQLITE_ENABLE_MATH_FUNCTIONS`, `_WIN32`, `__GNUC__`, `SQLITE_DISABLE_INTRINSIC`, and optional `SQLITE_INDEX_SCAN_HEX`.
- c-pp public/internal APIs: `cmpp`, `cmpp_dx`, `cmpp_d_reg`, `cmpp_arg`, `cmpp_b`, `cmpp_api_init()`, `cmpp_dx_delim()`, `cmpp_tt_cstr()`, `cmpp_dx_err_check()`, `cmpp_dx_outf()`, `cmpp_dx_out_raw()`, `cmpp_dx_consume_b()`, `cmpp_b_chomp()`, `cmpp_b_clear()`, `cmpp_d_register()`, `cmpp_malloc()`, `cmpp_mfree()`, `cmpp_err_get()`, and `CMPP_MODULE_REGISTER1(demo)`.
- Standard C dependencies in the demo region: `stdlib.h`, `assert.h`, and `string.h`.

## Risks And Edge Cases

- `seriesFilter()` relies on the `idxNum` bitmask and argument ordering produced by `seriesBestIndex()`. Any future change to one side must preserve the exact bit meanings and `argv` order.
- Floating-point value constraints are subtle. Equality only returns rows for integral finite values in signed 64-bit range, while `>`/`<` with exact integer floats must move one integer past the bound. The local ceil/floor fallback must continue matching libc behavior for relevant finite values.
- Signed 64-bit overflow is intentionally avoided through unsigned helper operations. Replacing `span64()`, `add64()`, or `sub64()` with ordinary signed arithmetic would risk undefined behavior at `SMALLEST_INT64`/`LARGEST_INT64`.
- `iLimit` and `iOffset` are signed SQLite integers. Negative `OFFSET` has no effect because only `iOffset > 0` is applied; negative `LIMIT` behaves as unlimited because shortening only occurs for `iLimit >= 0`.
- In the `LIMIT` path, `seriesSteps(pCur) > (sqlite3_uint64)iLimit` followed by `(iLimit - 1) * pCur->iStep` assumes the zero-limit case has been handled safely. This is an important boundary for tests because `iLimit == 0` can produce arithmetic that is easy to mishandle.
- The `seriesBestIndex()` check `if( aIdx[3]==0 )` appears intended to ignore `OFFSET` without `LIMIT`, but `aIdx[3]` is initialized to `-1`. That condition only fires if the chosen LIMIT constraint is at index 0, so reviewers should verify whether this is inherited SQLite behavior, a transcription issue, or an actual bug in this combined source.
- `seriesBestIndex()` marks constraints omittable for `i>=3`, so `LIMIT`, `OFFSET`, and value constraints may be enforced by the virtual table instead of the core. Incorrect range math would therefore be directly visible as wrong query results.
- The c-pp `divOpener()` writes argument text directly into a single-quoted HTML class attribute without escaping. This is acceptable for a demonstration directive only if callers treat arguments as trusted class names.
- `cmpp_dx_f_divClose()` reports misuse if a closer appears without a matching opener in the shared directive state, but the state is per registered directive, not per nested parser stack beyond the integer counter.
- `cmpp_dx_f_divWrapper()` depends on `dx->d->closer` being correctly registered. A mismatched closer descriptor would make block consumption stop at the wrong directive or fail to stop.

## Test Signals

- `SELECT value FROM generate_series(1,5,2)` should yield `1,3,5`, and hidden columns should report the original `start`, `stop`, and `step`.
- Descending scans such as `generate_series(5,1,-2)` and ascending `ORDER BY` over a descending input should verify base/term swapping and `bDesc` handling.
- Queries with `WHERE value BETWEEN ...`, `value = ...`, `value > ...`, and `value < ...` should confirm that the first generated value is aligned to the step and that terminal values are snapped to reachable values.
- Floating-bound tests should cover integral floats, non-integral floats, values beyond signed 64-bit range, and strict comparison at exact integers.
- Boundary tests should include `SMALLEST_INT64`, `LARGEST_INT64`, negative `SMALLEST_INT64` step magnitude, zero step normalization to one, empty directionally impossible ranges, NULL constraints, `LIMIT 0`, positive `LIMIT`, positive `OFFSET`, and `OFFSET` without `LIMIT`.
- Planner tests should verify missing-start errors when `ZERO_ARGUMENT_GENERATE_SERIES` is not defined, acceptance of usable rowid/value constraints as a substitute, rejection of unusable hidden-column constraints, and `ORDER BY value ASC/DESC` consumption.
- Extension tests should confirm `sqlite3_series_init()` registers `generate_series` on modern SQLite builds and returns the documented version error for runtimes older than 3.8.12.
- c-pp demo tests should exercise `demo1` argument dumping, `demo-div` open/close balance, misuse of a dangling closer, `demo-div-wrapper` with nested directives, autoload lookup for opener and closer names, and destructor cleanup for allocated directive state.
