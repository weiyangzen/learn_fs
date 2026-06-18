# Research: sources/sync-backup/syncthing/test/folders.sh

## sources/sync-backup/syncthing/test/folders.sh

Purpose: emits XML folder configuration blocks for a large number of fake folders.

Important APIs/functions: Bash C-style loop from `id=0` to `199`, with a here-document generating `<folder>` entries.

Control flow: for each numeric id, prints a sendreceive folder using fake filesystem path parameters `maxsize=1000` and `seed=<id>`, disabled watcher, two device IDs, and common folder settings.

State and persistence: no direct file writes; intended output can be redirected into a config.

Dependencies and integration: Bash and Syncthing XML config format. Risks are static device IDs and XML schema drift. Test signal is use in performance or many-folder fixture generation.
