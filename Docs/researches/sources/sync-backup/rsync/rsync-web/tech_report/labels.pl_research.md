# sources/sync-backup/rsync/rsync-web/tech_report/labels.pl

Purpose: LaTeX2HTML support data for labels in the rsync technical report.

Important APIs, types, and functions: Defines `%external_labels`, `%noresave`, `%ref_files`, and `%noresave` entries for labels such as `fig:pipeline`, then returns true with `1;`.

Control flow: Static Perl assignments only.

State and persistence behavior: No mutation beyond populating package-global hashes at load time. It serves generated documentation navigation/reference state.

Dependencies and integration points: Consumed by the technical report HTML generation output. Must remain in sync with generated HTML files.

Risks and test signals: Risk is stale or missing labels after documentation regeneration. Test by loading the generated report and checking internal references.
