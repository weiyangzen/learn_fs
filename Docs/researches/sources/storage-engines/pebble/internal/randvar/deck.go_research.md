<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/deck.go -->
# sources/storage-engines/pebble/internal/randvar/deck.go

Purpose: implements a weighted random generator using a shuffled deck so each weight appears exactly its configured number of times per deck cycle.

Important APIs/types: `Deck`, `NewDeck`, and `Int`.

Control flow and state: `NewDeck` expands integer weights into a slice containing each index repeated by its weight, stores an RNG through `ensureRand`, and sets the index to the deck length so the first `Int` shuffles. `Int` locks, reshuffles when the deck is exhausted, returns the current card, advances the index, and unlocks.

Persistence and integration: state is in-memory and concurrency-safe around the deck. It integrates with `math/rand/v2` and local `NewRand`. Risks include panic if all weights sum to zero because `Int` indexes an empty deck, no validation for negative weights, and holding the mutex during shuffle. The test samples values but does not assert distribution.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/deck.go -->
