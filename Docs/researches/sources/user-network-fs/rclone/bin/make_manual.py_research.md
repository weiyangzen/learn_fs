# sources/user-network-fs/rclone/bin/make_manual.py

Purpose: builds the monolithic `MANUAL.md` by concatenating selected Hugo markdown docs and generated command docs, normalizing front matter, shortcodes, icons, image URLs, and absolute links. It also embeds `rclone help` output and uses `SOURCE_DATE_EPOCH` for reproducible build dates.

Important functions: `read_doc`, `check_docs`, `read_command`, `read_commands`, and `main`. State changes are writes to `MANUAL.md`. Dependencies include doc file ordering, `rclone` in PATH, commands docs, and regex transformations for Hugo shortcodes. Risks include strict front matter splitting, docs list drift, duplicated docs entry (`protondrive.md` appears twice), broad shortcode regex removal, and failures when docs exist on disk but not in `docs`. Test signal is successful generation plus downstream manual/manpage build checks.
