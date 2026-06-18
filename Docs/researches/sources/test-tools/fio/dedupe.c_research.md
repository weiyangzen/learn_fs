# sources/test-tools/fio/dedupe.c

Purpose: Initializes deterministic seed arrays used by fio's dedupe working-set data generation mode, including optional global dedupe across jobs.

Important APIs/functions: `init_global_dedupe_working_set_seeds()` iterates all thread jobs that request global dedupe. `init_dedupe_working_set_seeds(struct thread_data *td, bool global_dedup)` allocates and fills `td->dedupe_working_set_states`.

Control flow: The per-thread initializer exits unless dedupe percentage is set and mode is `DEDUPE_MODE_WORKING_SET`. It computes how many RNG advancements correspond to one write block, derives the number of unique pages from job size and working-set percentage, allocates an array of `frand_state`, copies the thread buffer state as the first seed, then advances and records seeds for each unique page. In global mode it periodically switches the source seed to another thread's `buf_state` so duplicate buffers can span jobs.

State/persistence: Persists allocated seed arrays and `num_unique_pages` on `thread_data`. The global initializer relies on all jobs' seeds already being initialized.

Dependencies/integration: Uses fio job iteration, random state helpers, compression chunk sizing, block size options, and global `thread_number`/`tnumber_to_td()`.

Risks: If `num_unique_pages` computes to zero, the code allocates zero bytes then writes index zero, which is a likely bug for tiny sizes or zero percentages after integer truncation. Global distribution depends on stable thread numbering and initialized `buf_state`. Memory cleanup is outside this file.

Test signals: Test tiny jobs, compression chunk interactions, single-thread and multi-thread global dedupe, and deterministic repeatability of generated buffers.
