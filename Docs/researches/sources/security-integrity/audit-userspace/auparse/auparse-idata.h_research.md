# sources/security-integrity/audit-userspace/auparse/auparse-idata.h

Purpose: Internal interpretation data contract between auparse record parsing and field interpretation lookup code.

Important APIs, types, and functions: Defines `idata`, carrying machine type, syscall, syscall arguments `a0`/`a1`, current working directory, field name, and field value. Declares interpretation helpers `auparse_interp_adjust_type()`, `auparse_do_interpretation()`, `_auparse_load_interpretations()`, `_auparse_free_interpretations()`, `_auparse_lookup_interpretation()`, and `_auparse_flush_caches()`. Defines `NEVER_LOADED`.

Control flow: Header-only declarations; implementation flow lives in `interpret.c`, `auparse.c`, and lookup code. The structure is populated from `rnode` data produced by `ellist.c`.

State and persistence: No state in this header. Interpretation caches and lists are stored in `auparse_state_t`.

Dependencies and integration points: Includes `config.h`, `dso.h`, `auparse.h`, and `auparse-defs.h`. Used by internal but exported-hidden interpretation paths.

Risks and edge cases: `idata` contains borrowed pointers (`cwd`, `name`, `val`), so interpretation code must not outlive the record/cursor data. Machine/syscall values may be unknown or sentinel values from parsing failures.

Test signals: Interpretation tests and search tests using interpreted fields exercise this contract indirectly.
