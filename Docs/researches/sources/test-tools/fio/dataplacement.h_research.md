# sources/test-tools/fio/dataplacement.h

Purpose: Defines fio data placement constants, selection modes, state structures, and public functions.

Important APIs/types: Constants include `STREAMS_DIR_DTYPE`, `FDP_DIR_DTYPE`, `FIO_MAX_DP_IDS`, and `DP_MAX_SCHEME_ENTRIES`. Mode enums define random/round-robin/scheme selection and none/FDP/streams placement type. Structures are `fio_ruhs_info`, `fio_ruhs_scheme_entry`, and `fio_ruhs_scheme`. Public APIs mirror `dataplacement.c`.

Control flow: Headers provide contracts for initialization, cleanup, and per-IO directive fill; callers must call `dp_init()` before `dp_fill_dspec_data()` can attach directives.

State/persistence: `fio_ruhs_info` uses a flexible array for PLIs and tracks current round-robin position. Scheme state is a fixed array of at most 32 entries.

Dependencies/integration: Includes `io_u.h`, so it participates directly in fio IO unit definitions.

Risks: `FIO_MAX_DP_IDS` and `DP_MAX_SCHEME_ENTRIES` are fixed compile-time caps. The flexible array requires careful allocation sizing by users.

Test signals: Compile-time integration should ensure `fio_file` and `io_u` users agree on these structures; runtime tests should exercise all selection modes.
