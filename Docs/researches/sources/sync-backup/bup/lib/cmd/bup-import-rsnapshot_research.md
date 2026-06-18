## sources/sync-backup/bup/lib/cmd/bup-import-rsnapshot

Purpose: imports rsnapshot-style directory snapshots into Bup branches.

Important APIs and control flow: supports dry-run, validates a snapshot root plus optional target branch, changes to the snapshot root, then iterates snapshot directories and branch subdirectories. For each selected branch, it obtains ctime using Perl `stat`, indexes the branch path into `bupindex.$BRANCH.tmp`, and saves with `--strip --date=$DATE -n $BRANCH`.

State and dependencies: writes temporary index files in the snapshot root and persists data through Bup repo objects/refs. It depends on `basename`, `perl`, shell globbing, and the local `bup` wrapper.

Risks and tests: branch names are used in temp index filenames without sanitization, so odd names can collide or create awkward paths. It uses ctime rather than snapshot directory names. There is no listed direct test in this subset; behavior is analogous to rdiff/duplicity import tests.
