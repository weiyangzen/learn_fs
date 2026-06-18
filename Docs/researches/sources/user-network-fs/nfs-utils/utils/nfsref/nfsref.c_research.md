## sources/user-network-fs/nfs-utils/utils/nfsref/nfsref.c

Purpose: Main command dispatcher for `nfsref`, managing root checks, global options, junction type selection, and subcommand routing.

Important APIs/types/functions: Defines option tables for `--debug`, `--help`, and `--type`; `nfsref_usage`; and `main`. Supported subcommands are `add`, `remove`, and `lookup`.

Control flow: `main` initializes locale, umask, logging, parses options, rejects non-root execution except help, chooses the subcommand, and calls the corresponding implementation. Successful add/remove operations flush the exports cache.

State and persistence: Does not store state directly; operations invoked by it mutate junction metadata and export cache state.

Dependencies and integration: Uses `junction_flush_exports_cache`, `xlog`, and declarations in `nfsref.h`.

Risks and test signals: Option parsing permits help before root enforcement, but subcommand argument boundaries need coverage. Tests should validate `-t nfs-basic`, rejected type strings, missing parameters, root permission checks, and cache flush calls after mutations.
