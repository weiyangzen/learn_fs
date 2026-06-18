# sources/sync-backup/kopia/internal/scheduler/scheduler.go

Purpose: runs a lightweight scheduler that periodically asks for upcoming items and triggers due callbacks.

Important APIs/types/functions: `GetItemsFunc`, `Item`, `Scheduler`, `Options`, `Start`, `upcomingItems`, `Stop`, `run`, and `TriggerNames`.

Control flow: `Start` creates a scheduler goroutine. Each loop calls `getItems`, partitions due items from future items, triggers due callbacks, then sleeps until the nearest future time, a refresh signal, or stop. With no upcoming items it sleeps for a long default interval.

State and persistence behavior: in-memory goroutine, stop channel, refresh channel, time function, and item source. It persists nothing externally.

Dependencies and integration points: server uses it for repository refresh, maintenance, and scheduled snapshots.

Risks and test signals: timer/refresh races and past-due handling are key. Tests validate scheduling, past triggers, refresh behavior, and trigger-name formatting.
