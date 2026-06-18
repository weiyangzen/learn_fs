# sources/sync-backup/rsync/rsync-web/tech_report/images.pl

Purpose: LaTeX2HTML support data mapping image keys to generated image files and metadata for the rsync technical report.

Important APIs, types, and functions: Defines Perl hashes such as `%cached_env_img`, `%cached_env_img_width`, `%cached_env_img_height`, `%cached_env_img_align`, `%cached_env_img_alt`, and `%cached_env_img_map`. Entries map symbolic labels like `displaymath62` to image filenames, dimensions, alignment, alt text, and image-map flags.

Control flow: No executable flow beyond Perl assignment and final `1;` module truth value.

State and persistence behavior: Provides static metadata to a consuming Perl/LaTeX2HTML pipeline. It does not write files.

Dependencies and integration points: Loaded by generated technical-report HTML tooling. Depends on the corresponding image files being present.

Risks and test signals: Risks are stale image dimensions, missing image files, or broken alt text after report regeneration. Test by loading the file in Perl and rendering the technical report to ensure every referenced image resolves.
