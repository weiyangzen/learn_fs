# sources/test-tools/fio/profile.h

Purpose: public profile plugin interface for fio.

Important APIs/types: `struct prof_io_ops` exposes optional `td_init`, `td_exit`, and `io_u_lat` hooks. `struct profile_ops` describes a profile with list linkage, name, description, options, option storage, `prep_cmd()`, generated command line, and optional IO hooks. Declares registration, lookup, loading, hook installation, and td lifecycle helpers.

Control flow and state: no implementation, but defines the contract consumed by `profile.c` and profile modules under `profiles/`.

Dependencies and integration: includes `flist.h` and uses `struct fio_option` and `struct thread_data` from broader fio headers.

Risks: fixed-size `name[32]` and `desc[64]` require profile authors to keep identifiers short. `cmdline` must be stable and NULL-terminated.

Test signals: compile profile modules and run profile load paths with custom options and hooks.
