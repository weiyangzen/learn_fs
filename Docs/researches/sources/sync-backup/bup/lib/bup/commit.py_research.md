# sources/sync-backup/bup/lib/bup/commit.py

## Purpose
`commit.py` parses and constructs Git commit metadata used by bup save/get/split and annotates bup-created commits with version and argv trailers.

## APIs and Control Flow
`parse_tz_offset` converts `+HHMM`/`-HHMM` to seconds. `parse_commit_gpgsig` removes Git continuation formatting. Regex constants define accepted safe author/committer fields, parents, mergetag, optional gpgsig, and message. `CommitInfo` stores parsed fields. `parse_commit` matches the regex and returns typed fields. `_local_git_date_str`, `_git_date_str`, and `create_commit_blob` format commit headers. `has_trailers` detects a trailer block. `commit_message` appends `Bup-Version`, shell-encoded `Bup-Argv`, and optional ASCII trailers, inserting a blank line when needed.

## State, Dependencies, Integration, Risks, Tests
The module is pure except for importing current bup `version`. It depends on regex correctness, `utc_offset_str`, and `enc_sh`. It integrates with `save`, `split`, `get`, and remote ref-vetting in `on.py`. Risks include incomplete Git commit grammar coverage, mergetag/gpgsig assumptions, strict safe string regex rejecting valid commits, and trailer detection differing from Git's full interpreter. Test signals include parsing commits with multiple parents, timezone signs, gpgsig continuation, message trailers, create/parse round trips, and argv shell encoding.
