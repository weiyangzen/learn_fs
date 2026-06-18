# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/433

Purpose: Linux reporter parse fixture for syzkaller. It expects the same `INFO: task hung in synchronize_rcu` title and expedited alternates, type `HANG`, corrupted `N`, panicked `Y`. This variant is a packet socket bind path blocked in `synchronize_net`.

Important APIs, types, and functions: key frames include `synchronize_rcu_expedited`, `synchronize_net`, `__unregister_prot_hook`, `packet_do_bind`, `packet_bind`, `__sys_bind`, and `__x64_sys_bind`.

Control flow: 50 log lines are parsed. The parser must keep the synchronization hang title, not specialize to packet bind, while producing the same alternates as related RCU fixtures.

State and persistence behavior: fixture headers store expected fields; parsing is read-only and transient.

Dependencies, integration points, risks, and test signals: this protects stable deduplication across different callers blocked on expedited RCU. Risks are splitting by packet socket frames. Passing tests require HANG type, panic flag, exact alternates, and non-corruption.
