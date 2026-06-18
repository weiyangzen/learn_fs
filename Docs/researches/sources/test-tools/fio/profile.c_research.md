# sources/test-tools/fio/profile.c

Purpose: profile registration, lookup, option injection, and per-thread profile hooks for fio benchmark profiles.

Important APIs/functions: `find_profile()`, `load_profile()`, `register_profile()`, `unregister_profile()`, `profile_add_hooks()`, `profile_td_init()`, and `profile_td_exit()`.

Control flow: profiles are stored in a global intrusive list. `register_profile()` annotates profile-specific options with `prof_name` and `prof_opts`, registers them with the global option system, links the profile, and adds the profile name as a valid value for the `profile` option. `load_profile()` finds a profile, calls `prep_cmd()`, then adds the generated command-line options. `profile_add_hooks()` copies optional `prof_io_ops` into a `thread_data` when a profile is active.

State and persistence: static `profile_list` holds registered profiles. Profile option metadata is mutated during registration and invalidated during unregister. `thread_data` receives copied hook operations and a flag.

Dependencies and integration: `fio.h`, option system (`add_option`, `add_job_opts`, `add_opt_posval`, invalidation helpers), debug/logging, and `flist`.

Risks: registration mutates shared static option tables; unregister must cleanly remove option values. `load_profile()` assumes `prep_cmd()` produced a NULL-terminated command line. Hook copying means later changes to the profile ops are not reflected in already initialized threads.

Test signals: registering/unregistering profiles, profile-specific option parsing, missing profile errors, prep failures, and td init/exit hook execution.
