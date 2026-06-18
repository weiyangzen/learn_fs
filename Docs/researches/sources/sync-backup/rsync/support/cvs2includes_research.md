<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/cvs2includes -->
# sources/sync-backup/rsync/support/cvs2includes

Purpose: generate `.cvsinclude` rsync filter files from CVS metadata so `--cvs-exclude` transfers still include checked-in files and directories.

Important APIs/types/functions: `main()` walks the tree, reads `CVS/Entries`, writes `.cvsinclude`, and removes stale include files. `INC_NAME` is `.cvsinclude`.

Control flow: optionally chdir to the supplied root, walk all subdirectories, remember existing `.cvsinclude` files, detect `CVS/Entries`, parse entries beginning with `/` or `D/`, write `+ /name` include lines next to the CVS directory when content changed, sort child directories for deterministic traversal, and delete include files not regenerated from current CVS metadata.

State and persistence behavior: mutates `.cvsinclude` files throughout the working tree. It avoids rewriting unchanged content but deletes stale generated files.

Dependencies and integration points: depends on Python 3 and CVS `Entries` file format. The generated files are consumed by rsync filters such as `-f ': .cvsinclude'` or `.rsync-filter` includes.

Risks: it assumes CVS entry syntax and does not preserve manual edits in `.cvsinclude` files that are considered stale. Running it in the wrong directory can create or delete include files broadly.

Test signals: create sample `CVS/Entries` files and stale `.cvsinclude` files, run the script, and confirm deterministic include lines, unchanged-file reporting, and stale-file removal.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/cvs2includes -->
