## sources/user-network-fs/blobfuse2/copyright_fix.sh

Purpose: Maintenance script for adding or replacing Go source copyright/license headers and updating copyright years from `LICENSE`.

Important flow: It derives `currYear` from `date`, extracts the license line containing `Copyright ©`, and scans `find -name *.go`. With argument `replace`, it replaces fixed line ranges using `sed` depending on whether `+build` appears. Without `replace`, it adds a header to Go files missing the copyright marker, or updates the marker line when the current year is absent.

State and persistence: Mutates Go files in place and uses a temporary file named `__temp__` in the current directory. Reads the repository `LICENSE`.

Dependencies and integration: Uses Bash, `find`, `grep`, `sed`, `tail`, `cat`, and `mv`. Intended for repository-wide maintenance rather than runtime.

Risks: The line-range edits assume stable header lengths and can damage files with unusual build tags or comments. Unquoted variables break on spaces. The temp filename can collide. Search is repository-wide and not scoped to tracked files. No tests are present; validation would require diff inspection after running.
