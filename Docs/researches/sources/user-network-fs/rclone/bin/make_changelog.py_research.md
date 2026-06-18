# sources/user-network-fs/rclone/bin/make_changelog.py

Purpose: generates a new top section for `docs/content/changelog.md` from git commit subjects between two version refs. It categorizes commits by prefix, normalizes backend aliases, strips issue references, splits remaining items into new features versus fixes, and writes a complete changelog to stdout.

Important functions: `process_log` parses `git log --pretty` lines into category buckets; `make_out` renders selected categories; `main` reads old changelog, updates build date, inserts compare link and generated sections. State is stdout only unless caller redirects. Dependencies are git, docs layout, backend directory names, regex conventions in commit subjects. Risks include malformed commit messages containing unexpected `|`, category misclassification, duplicate `protondrive.md` elsewhere not relevant here, and manual release-edit needs. Test signal is manual review of generated changelog.
