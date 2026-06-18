# sources/user-network-fs/samba/source3/script/updatekeytab_test.sh

Purpose: callout script used by clustered keytab selftests to run `net ads keytab create` on every local CTDB test daemon node.

Important functions and APIs: delegates to `./ctdb/tests/local_daemons.sh "$PREFIX/clusteredmember" onnode all 'net ads keytab create --option="sync machine password script=" --configfile=$CTDB_BASE/lib/server.conf'`.

Control flow: no argument parsing or functions. It executes one CTDB helper command, which invokes `onnode all` for the clustered member prefix.

State and persistence: causes each node to create/update its keytab via `net ads keytab create`; the script itself creates no files.

Dependencies and integration: installed temporarily by `test_update_keytab_clustered.sh` as the `sync machine password script`. Depends on `PREFIX`, CTDB local daemon layout, `local_daemons.sh`, `onnode`, and `$CTDB_BASE` in the command evaluated on nodes.

Risks and test signals: the relative path assumes the current working directory is Samba source root. There is no explicit error handling beyond shell exit status. Its main signal is whether the caller sees synchronized node keytabs.
