# sources/user-network-fs/rclone/cmd/rmdirs/rmdirs.go

Purpose: implements `rclone rmdirs`, recursively removing empty directories under a path.

Important APIs/state: flags for leaving root behavior (package global in file) and Cobra command; delegates to `operations.Rmdirs`/related empty-dir removal helper.

Control flow: validates one remote path, creates source/directory Fs, and runs the recursive empty-directory removal in a mutating command context. Help explains root behavior and backend limitations.

State/persistence: destructive only for empty directories; can remove many remote directory markers. Dependencies are operations and command flags. Risks include virtual-directory backends, race with concurrent writers, and user expectations around root removal. Test signal is likely operations-level.
