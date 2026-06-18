# sources/user-network-fs/rclone/bin/update-authors.py

Purpose: updates `docs/content/authors.md` with contributors found in git history, committing each new author entry. It considers both commit author emails and `Co-authored-by:` trailers, excluding emails already present or listed in `bin/.ignore-emails`.

Important functions: `load`, `add_email`, and `main`. State changes are appending to authors docs and creating git commits. Dependencies are git, author file format, ignore file format, and commit trailer conventions. Risks include one commit per author, no dry-run mode, no dirty-tree guard, name/email parsing by simple delimiters, and possible duplicate people with different emails. Test signal is resulting commits and reviewed authors diff.
