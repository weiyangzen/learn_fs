<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/external/example.sh -->
# sources/sync-backup/git-annex/doc/special_remotes/external/example.sh

Purpose: full shell example of a git-annex external special remote, modeled on the built-in directory remote and demonstrating configuration, credentials, transfer, presence, removal, export, rename, and info protocol messages.

Important functions: `runcmd` redirects command stdout to stderr to preserve the line protocol. `ask`, `getconfig`, and `setconfig` implement synchronous protocol queries. `calclocation` asks git-annex for `DIRHASH` and stores keys under `$mydirectory/$RET/$key`. `setupcreds` and `getcreds` demonstrate `SETCREDS`/`GETCREDS`. `dostore`, `doretrieve`, `docheckpresent`, and `doremove` implement object operations with protocol success/failure responses.

Control flow: emits `VERSION 2`, then loops over stdin. `LISTCONFIGS` advertises `directory`. `INITREMOTE` resolves and stores an absolute directory, creates it, and records credentials. `PREPARE` retrieves credentials and configuration before normal use. `TRANSFER STORE` writes via a temp file under `$mydirectory/tmp` then atomically moves into place. `TRANSFER RETRIEVE`, `CHECKPRESENT`, and `REMOVE` operate by key-derived locations. Export requests use an `exportlocation` set by `EXPORT` and implement transfer, presence, removal, directory removal, and rename semantics.

State and persistence: persistent state is the configured storage directory, files stored under hashed key paths, export paths, and git-annex-managed credentials/config. Runtime variables include `mydirectory`, `LOC`, `RET`, and `exportlocation`.

Dependencies and integration points: POSIX shell plus common tools (`readlink`, `sed`, `cp`, `mv`, `rm`, `mkdir`, `dirname`). It must be installed as `git-annex-remote-directory` or another external type name and is driven entirely by git-annex's external special remote protocol.

Risks: `set -- $line` and many unquoted protocol fields cannot safely represent all filenames/keys with whitespace, though later `file="$@"` mitigates some transfer path cases. `rmdir "$mydirectory/tmp"` can fail if concurrent transfers share the same temp directory. `REMOVEEXPORTDIRECTORY` checks `[ ! -d "$dir" ]` instead of `$mydirectory/$dir`, which is a path confusion risk in the example. Credential demo intentionally requires environment variables during initremote.

Test signals: protocol transcript tests for every request, idempotent `INITREMOTE`, store/retrieve/remove round trips, unavailable-directory `CHECKPRESENT-UNKNOWN`, export store/retrieve/rename/remove, and concurrent transfer behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/external/example.sh -->
