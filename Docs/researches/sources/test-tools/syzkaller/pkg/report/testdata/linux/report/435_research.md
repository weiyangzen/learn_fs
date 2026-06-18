# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/435

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in synchronize_rcu`, alternates for `__synchronize_srcu` and hang wording, type `HANG`, corrupted `N`, panicked `Y`. The body covers fsnotify mark destruction blocked in SRCU synchronization.

Important APIs, types, and functions: this tests hung-task handling for SRCU/RCU naming variants. Frames include `wait_for_completion`, `__synchronize_srcu`, `synchronize_srcu`, `fsnotify_mark_destroy_workfn`, `process_one_work`, and worker thread helpers.

Control flow: 128 log lines are parsed. The reporter must generate alternates that include the SRCU internal function while normalizing the primary title to `synchronize_rcu`.

State and persistence behavior: expected alternates and panic flag are stored in headers. Runtime state is transient hang parsing.

Dependencies, integration points, risks, and test signals: this protects hang grouping for fsnotify SRCU cleanup. Risks include losing the SRCU alternate or selecting worker helpers. Passing tests require the primary/alternate set, HANG type, panic `Y`, and non-corruption.
