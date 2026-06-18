# sources/storage-engines/sqlite/ext/fts3/fts3_snippet.c

## Purpose

Implements FTS3/FTS4 auxiliary result functions `snippet()`, `offsets()`, and `matchinfo()`, plus shared phrase iteration and matchinfo-buffer caching. It turns expression evaluation doclists and row text into user-visible highlight snippets, byte offsets, and ranking/statistics blobs.

## Important APIs, types, and functions

Public entry points are `sqlite3Fts3Snippet()`, `sqlite3Fts3Offsets()`, `sqlite3Fts3Matchinfo()`, `sqlite3Fts3ExprIterate()`, and `sqlite3Fts3MIBufferFree()`. Key types include `LoadDoclistCtx`, `SnippetIter`, `SnippetPhrase`, `SnippetFragment`, `MatchInfo`, `MatchinfoBuffer`, `StrBuffer`, `LcsIterator`, `TermOffset`, and `TermOffsetCtx`. Important helpers include `fts3BestSnippet()`, `fts3SnippetText()`, `fts3SnippetShift()`, `fts3MatchinfoValues()`, `fts3GetMatchinfo()`, `fts3MatchinfoLcs()`, `fts3ExprLHitGather()`, and `fts3ColumnlistCount()`.

## Control flow

Phrase iteration skips the right side of `NOT` expressions. Snippet generation loads phrase doclists, gathers per-column position lists, scores candidate token windows by phrase coverage and hit count, expands up to four fragments, then retokenizes row text to emit highlighted text and ellipses. Offsets count query terms, initializes position iterators per column, retokenizes stored column text, and appends `column term start length` tuples. Matchinfo validates the format string, allocates or reuses a cached two-slot buffer, computes global fields once per query, and fills row-local fields for each current row.

## State and persistence

Most state is per-call heap memory, but `Fts3Cursor.pMIBuffer`, `nPhrase`, and `isMatchinfoNeeded` cache matchinfo state across rows. The code reads persisted FTS segment/doclist data, `%_docsize`, `%_stat`/doctotal records, and content columns through the current cursor statement, but does not write persistent state.

## Dependencies and integration points

Depends heavily on FTS evaluation APIs from `fts3Int.h`: `sqlite3Fts3EvalPhrasePoslist()`, `sqlite3Fts3EvalPhraseStats()`, `sqlite3Fts3EvalTestDeferred()`, `sqlite3Fts3SegmentsClose()`, `sqlite3Fts3SelectDoctotal()`, `sqlite3Fts3SelectDocsize()`, `sqlite3Fts3MsrCancel()`, and FTS varint helpers. It uses the table tokenizer to map token positions back to source byte offsets.

## Risks and test signals

Risks include corrupt doclists causing invalid varint walks, matchinfo format restrictions differing between FTS3 and FTS4, deferred-token approximations, stale cached global matchinfo after format changes, tokenizer offset mismatches, snippet masks limited to 64 tokens/phrases modulo 64, and contentless-table offset corruption detection. Test signals include exact `snippet()`, `offsets()`, and `matchinfo()` outputs, `pcx` default behavior, `l`, `a`, `n`, `s`, `x`, `y`, and `b` flags, deferred-token queries, NULL columns, corrupt-index tests, and multi-column/multi-fragment snippets.
