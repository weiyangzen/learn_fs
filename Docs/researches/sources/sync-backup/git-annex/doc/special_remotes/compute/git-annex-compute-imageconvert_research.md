<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-imageconvert -->
# sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-imageconvert

Purpose: git-annex compute remote program that uses ImageMagick `convert` to transform an input image into an output image requested by git-annex.

Important protocol behavior: validates two command-line arguments, prints `INPUT <arg1>` and reads the provided local input path, prints `OUTPUT <arg2>` and reads the output path, then runs `convert "$input" "$output"` when an input path was supplied. Conversion diagnostics are redirected to stderr to avoid corrupting stdout protocol messages.

Control flow and state: single transaction, no loop, no durable state. The compute remote protocol supplies concrete temporary paths in response to `INPUT`/`OUTPUT`.

Dependencies and integration points: POSIX shell, git-annex compute remote protocol, and ImageMagick's `convert` executable.

Risks: no explicit success/failure protocol response beyond process exit. It trusts ImageMagick to handle untrusted image data, which historically has had parser vulnerabilities. Missing input quietly skips conversion and exits successfully.

Test signals: run under git-annex compute with a known JPEG-to-GIF conversion, verify output content, check missing arguments, absent `convert`, and malicious/invalid input handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-imageconvert -->
