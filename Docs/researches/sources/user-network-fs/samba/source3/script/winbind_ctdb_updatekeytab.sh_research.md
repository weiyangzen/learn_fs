# sources/user-network-fs/samba/source3/script/winbind_ctdb_updatekeytab.sh

Purpose: CTDB-installed callout for winbind machine-password synchronization that refreshes AD keytabs on connected cluster nodes.

Important functions and APIs: executes `onnode -p connected "net ads keytab create --option='sync machine password script='"`. The `-p connected` selector limits the operation to connected nodes.

Control flow: no local branching; command exit status is the script exit status.

State and persistence: updates AD keytabs on selected nodes through `net ads keytab create`. Passing `sync machine password script=` disables recursive invocation of the same hook.

Dependencies and integration: installed by `source3/script/wscript_build` into the CTDB scripts directory when `conf.env.with_ctdb` is true. It depends on `onnode`, CTDB node state, and Samba `net` being in PATH in the CTDB script environment.

Risks and test signals: failures can be partial across nodes depending on CTDB connectivity. The script has no logging or retry logic itself; callers must inspect `onnode`/`net` output and exit status.
