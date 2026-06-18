# sources/test-tools/syzkaller/pkg/corpus/minimize.go

Purpose: Reduces the corpus to a smaller set of programs that preserves aggregate signal, with preference for simpler/non-squashed programs.

Important APIs/types/functions: `Corpus.Minimize`.

Control flow: Under corpus write lock, it builds `signal.Context` entries for all items, stable-sorts them to prefer items without squashed `any` arguments and then fewer calls, clears `progsMap` and all program lists, runs `signal.Minimize`, and repopulates maps/lists for retained items and their focus areas.

State and persistence behavior: Mutates in-memory corpus state destructively under lock. It does not recompute aggregate `signal` or `cover`, so those remain frontier totals, not minimized item sums.

Dependencies/integration points: Depends on `pkg/signal.Minimize` and `ProgramsList.saveProgram`.

Risks: The `cover bool` parameter is currently unused, which may surprise callers expecting coverage-aware minimization. Rebuilding focus area lists relies on each `Item.areas` map being complete.

Test signals: Invoked by `TestCorpusOperation`; deeper minimization correctness depends on `pkg/signal` tests and priority tests.
