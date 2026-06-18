# sources/test-tools/syzkaller/pkg/corpus/corpus.go

Purpose: Thread-safe in-memory corpus of syzkaller programs, aggregate signal/coverage, update notifications, statistics, and focus-area program lists.

Important APIs/types/functions: `Corpus`, `focusAreaState`, `FocusArea`, `NewCorpus`, `NewMonitoredCorpus`, `NewFocusedCorpus`, `ItemUpdate`, `Item`, `Item.StringCall`, `NewInput`, `NewItemEvent`, `Corpus.Save`, `applyFocusAreas`, `Signal`, `Items`, `Item`, `CallCover`, `ProgsPerArea`, and `Cover`.

Control flow: Constructors initialize maps, weighted program lists, focus areas, and stats. `Save` serializes and hashes a program, locks the corpus, either merges signal/coverage into an existing immutable-copy `Item` or creates a new one, applies focus areas based on coverage deltas, updates aggregate signal/coverage, and optionally sends a non-blocking/context-aware `NewItemEvent`.

State and persistence behavior: Corpus state is in memory behind `sync.RWMutex`: program map, aggregate signal, coverage, program lists, focus area lists, and stats. It emits serialized program bytes in update events but does not write files itself. `Item` objects are treated as immutable and replaced on updates.

Dependencies/integration points: Integrates `cover`, `signal`, `stat`, `hash`, and `prog`. Used by fuzzing components to save interesting programs and choose future mutation seeds.

Risks: `applyFocusAreas` initializes `item.areas` only inside the `nil` branch and immediately records one area; if an item later matches additional areas after `areas` is non-nil, that area is not recorded in `item.areas`, which can affect minimization repopulation. `Save` caps `Updates` at 32 to bound memory, losing later per-call update history.

Test signals: `corpus_test.go` covers basic save/update events, coverage delta reporting, stats, minimization call, and concurrent save/choose operations.
