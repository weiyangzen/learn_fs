# sources/user-network-fs/nfs-utils/support/nfs/conffile.c

Purpose: shared `nfs.conf`/`idmapd.conf` parser, in-memory configuration database, transaction queue, report generator, and targeted config-file writer.

Important APIs and types: public routines include `conf_init_file()`, `conf_cleanup()`, `conf_get_num()`, `conf_get_bool()`, `conf_get_str()`, `conf_get_section()`, `conf_get_entry()`, `conf_get_list()`, `conf_get_tag_list()`, `conf_free_list()`, `conf_begin()`, `conf_remove()`, `conf_remove_section()`, `conf_end()`, `conf_report()`, `conf_write()`, and `conf_decode_base64()`. `struct conf_binding` stores active section/arg/tag/value entries in 256 hash buckets. `struct conf_trans` queues set/remove operations by transaction id.

Control flow: `conf_init_file()` initializes tables, optionally loads `/usr/etc/...` before `/etc/...`, loads the main file, then scans `<file>.d` with `versionsort()` and only `*.conf` entries. `conf_readfile()` locks and reads a whole file. `conf_parse()` splits lines, handles backslash-newline folding, section headers with optional quoted subsection args, assignments with quoted/unquoted values, and recursive `include` or optional `include=-path`. Parsed assignments queue `CONF_SET` operations, then `conf_end(commit=1)` applies them to the hash table.

Mutation and persistence: active configuration lives in process-global hash buckets. Transactions live in a global `TAILQ` until committed or discarded. `conf_write()` opens or creates a config file, takes an exclusive `flock()`, reads content into output queues, updates comments or section/tag assignments in place semantically, truncates the file, and writes the rebuilt content. `modified_by` can append a timestamp comment.

Dependencies and integration: used by NFS support and nfsidmap code for configuration. Depends on `xlog`, BSD queue macros, file locks, `dirname()`, directory scanning, and config constants such as `NFS_CONFFILE`.

Risks: all state is global and unsynchronized. Includes can recurse without explicit cycle detection. `conf_get_section()` expands `$name` through the process environment or `[environment]` section and uses `goto retry`, so cyclic config references can loop. `conf_write()` truncates the original file after building queues but without a temp-file/rename strategy, so write failures can still damage the file despite locks. `conf_get_tag_list()` compares `arg` against `cb->arg` without checking `cb->arg` for NULL when `arg` is non-NULL.

Test signals: parse comments, quoted values, subsections, include and optional include, folded lines, duplicate tags, default-vs-override behavior, directory ordering, transaction rollback, list parsing, base64 validation, env expansion, config write add/update/delete, comments, folded values, and simulated write/truncate failures.
