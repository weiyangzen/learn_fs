# sources/test-tools/fio/zone-dist.h

Purpose: minimal public header for fio zone-distribution index lifecycle.

Important APIs/functions: declares `td_zone_gen_index(struct thread_data *td)` and `td_zone_free_index(struct thread_data *td)`.

Control flow/state: no implementation; callers allocate indexes before workloads that use `zone_split` and free them during teardown.

Dependencies/integration: relies on `struct thread_data` being visible or forward-declared by includers. Implemented by `zone-dist.c`.

Risks/test signals: because the header does not forward declare `struct thread_data`, include ordering matters. Compile coverage should include direct inclusion in translation units that already include fio core headers.
