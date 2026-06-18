# sources/storage-engines/sqlite/ext/fts5/fts5_tcl.c

## Purpose

`fts5_tcl.c` is test-only Tcl glue compiled under `SQLITE_TEST` and `SQLITE_ENABLE_FTS5`. It exposes FTS5 internals and extension APIs to SQLite's Tcl test suite. It lets tests obtain an `fts5_api` pointer from a Tcl database command, register Tcl-implemented auxiliary functions and tokenizers, invoke tokenizer APIs, inspect tokenizer locale state, toggle debug corruption assumptions, register additional test modules, and perform special test utilities such as dropping corrupt FTS5 tables.

## Important APIs, types, and functions

`f5tDbPointer()` extracts a `sqlite3*` from the Tcl SQLite command object using the leading layout of `SqliteDb`. `f5tDbAndApi()` prepares `SELECT fts5(?1)`, binds an `fts5_api_ptr`, and retrieves the FTS5 API. `F5tFunction`, `F5tApi`, and `F5tAuxData` support Tcl auxiliary functions and API subcommands.

`xF5tApi()` implements test wrappers for extension APIs: xColumnCount, xRowCount, xColumnTotalSize, xTokenize, xPhraseCount, xPhraseSize, xInstCount, xInst, xRowid, xColumnText, xColumnSize, xQueryPhrase, xSetAuxdata/xGetAuxdata including integer variants, phrase and phrase-column iteration, xQueryToken, xInstToken, and xColumnLocale. `xF5tFunction()` adapts an FTS5 auxiliary callback into a Tcl script invocation and returns Tcl results as SQLite values. `f5tCreateFunction()` registers such scripts through `fts5_api.xCreateFunction`.

Tokenizer test support includes `f5tTokenize()` for direct tokenization through a named tokenizer, `f5tCreateTokenizer()` for Tcl-defined tokenizers, `f5tTokenizerCreate()`, `f5tTokenizerTokenize_v2()`, `f5tTokenizerTokenize()`, `f5tTokenizerReturn()` (`sqlite3_fts5_token`), and `f5tTokenizerLocale()` (`sqlite3_fts5_locale`). Tokenizers may be v1 or v2, wrap a parent tokenizer, and expose locale values passed by core FTS5.

Additional commands include `sqlite3_fts5_may_be_corrupt`, `sqlite3_fts5_token_hash`, `sqlite3_fts5_register_matchinfo`, `sqlite3_fts5_register_fts5tokenize`, `sqlite3_fts5_register_origintext`, `sqlite3_fts5_drop_corrupt_table`, and `sqlite3_fts5_register_str`.

## Control flow

`Fts5tcl_Init()` creates Tcl commands and shares a `F5tTokenizerContext` with tokenizer-related commands. Auxiliary function registration stores the Tcl script and registers `xF5tFunction()` with FTS5. When SQLite invokes the auxiliary function, a temporary Tcl command representing the live `Fts5ExtensionApi` context is created, the user script is evaluated with that command and trailing SQL arguments, and the temporary command is deleted.

Tokenizer registration evaluates an instance-creation Tcl script during `xCreate`; that script returns the per-instance tokenization script. During tokenization, `f5tTokenizerReallyTokenize()` installs callback state in `F5tTokenizerContext`, appends the FTS5 tokenization mode and input text to the instance script, evaluates it, and expects the script to call `sqlite3_fts5_token` to emit tokens. If a parent tokenizer is configured, its tokens are fed back through `f5tTokenizeCallback()` so the Tcl script can transform parent tokens rather than raw input.

## State and persistence behavior

This file has no persistent database state of its own except for registered SQL functions, tokenizers, and virtual table modules attached to the database connection. Tcl object reference counts guard registered scripts and auxdata objects. Tokenizer context state is transient and only valid during a tokenizer callback; commands reject use outside that active callback. The debug `sqlite3_fts5_may_be_corrupt` command reads or mutates the global debug flag only in debug builds.

`sqlite3_fts5_drop_corrupt_table()` temporarily disables defensive mode, rewrites enough shadow-table state to make a corrupt FTS5 table droppable, drops it, and restores defensive mode. The `str()` test function returns a non-nul-terminated text buffer to exercise SQLite/FTS5 text-size handling.

## Dependencies and integration points

The file depends on Tcl, `tclsqlite.h`, `fts5.h`, SQLite C APIs, the FTS5 public extension API, and the test registration functions from `fts5_test_mi.c` and `fts5_test_tok.c`. It mirrors portions of the SQLite test harness internals by assuming the leading field of `SqliteDb` is `sqlite3 *db`. It is not built for release configurations.

## Risks and edge cases

The code intentionally bridges lifetimes across SQLite callbacks and Tcl command evaluation, making reference counts and destructor paths important. Temporary API Tcl commands hold stack `F5tApi` objects and must not outlive the callback. The tokenizer context is shared and restored around nested tokenization, so parent tokenizer recursion must preserve previous callback state. Error-code conversion from Tcl results to SQLite codes is deliberately narrow. The corrupt-drop utility mutates shadow tables and defensive mode and must remain test-only.

## Test signals

This file is itself a test surface. It enables direct assertions about extension API return values, auxdata destructor behavior, tokenizer callback flags, v1/v2 tokenizer compatibility, locale propagation to tokenizers and xColumnLocale, `xQueryToken`/`xInstToken`, content corruption handling, and auxiliary registration. The commands registered in `Fts5tcl_Init()` are the main Tcl-level probes for FTS5 behavior.
