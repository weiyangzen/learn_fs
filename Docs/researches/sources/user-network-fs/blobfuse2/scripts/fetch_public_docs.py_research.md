<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/fetch_public_docs.py -->
# sources/user-network-fs/blobfuse2/scripts/fetch_public_docs.py

## Purpose
Fetches selected Microsoft Learn Blobfuse2 pages and converts them to Markdown files under `public/`.

## Important APIs, Types, and Functions
`DOCS` maps output Markdown names to Learn URLs. The script creates `public`, configures `html2text.HTML2Text`, requests each URL with a 30 second timeout, converts HTML to Markdown, and writes each file.

## Control Flow and State
All work occurs at top level. Existing files with the same names are overwritten. There is no persistent cursor.

## Dependencies and Integration Points
Depends on `requests`, `html2text`, network access to Microsoft Learn, and local filesystem write access. The generated public docs are likely used by support/agent grounding.

## Risks and Edge Cases
No retry/backoff is implemented. HTML-to-Markdown conversion may include navigation or boilerplate. The fetched docs are time-dependent, so outputs can change across runs.

## Test Signals
Successful console messages and generated Markdown files signal completion. Content quality requires manual review or post-processing checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/fetch_public_docs.py -->
