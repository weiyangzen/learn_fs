# File Research: sources/os/plan9/9front/sys/src/cmd/git/export

rc script for exporting commits as patch emails/files.

Key responsibilities:
- Resolves a query to commits.
- Builds patch mail headers from commit author, commit message, and timestamp.
- Diffs each commit against its parent using scratch binds.
- Writes patches to stdout or `-o` patch directory.
- Generates numbered patch filenames from sanitized first-line subjects.

Important behavior:
- Uses `[PATCH]` or `[PATCH n/m]` subjects.
- Includes a 9front signature marker after diff content.
- Tolerates failure to create `/mnt/scratch` for web UI usage.

Notable risks:
- Uses `diff -ur` over bound trees rather than git-specific rename or mode metadata handling.
