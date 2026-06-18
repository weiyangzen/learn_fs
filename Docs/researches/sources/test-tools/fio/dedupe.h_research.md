# sources/test-tools/fio/dedupe.h

Purpose: Declares dedupe working-set seed initialization helpers.

Important APIs/types: Exports `init_dedupe_working_set_seeds(struct thread_data *td, bool global_dedupe)` and `init_global_dedupe_working_set_seeds(void)`.

Control flow: The caller initializes per-job or global dedupe state after job seeds are available and before data generation that needs the working set.

State/persistence: No state is declared in the header; state is stored in `thread_data`.

Dependencies/integration: Relies on `struct thread_data` and `bool` from fio headers included before this header.

Risks: The header does not include its own type dependencies, so include order matters.

Test signals: Build tests should include it from typical fio compilation units; runtime tests should validate seed setup before workload start.
