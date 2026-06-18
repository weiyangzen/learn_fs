# sources/sync-backup/git-lfs/t/t-path.sh

Purpose: security regression tests ensuring Git LFS does not execute a malicious `git` or PATHEXT-derived binary from the current working directory when resolving Git or credential-helper commands.

Important APIs/functions: uses `lfstest-badpathcheck`, `$BINPATH`, `$X`, `PATHEXT`, `PATH`, `GODEBUG=execerrdot=0`, `git lfs env`, `git lfs pull`, `git lfs uninstall/install`, credential-helper execution paths, and file checks for an `exploit` marker.

Control flow: the first test places a malicious `git` in the repo and runs `git-lfs env` with a restricted PATH, then asserts no exploit output or file appears. The credential test commits the malicious binary into an LFS repo, reclones with smudge disabled by temporarily uninstalling LFS, then runs `git-lfs pull` from a checkout containing the malicious binary to catch both general Git lookup and credential-helper lookup. The Windows-only PATHEXT test creates dummy `git.exe` and malicious `.exe`-style files to ensure fallback extension probing does not execute the wrong file.

State/persistence behavior: the tests deliberately create and sometimes commit suspicious executables, remove them from the worktree, and inspect generated logs plus the absence of an `exploit` file. The intended persistent state is normal LFS object storage, not execution side effects.

Dependencies/integration points: depends on Go `os/exec` path behavior, Git for Windows PATHEXT semantics, credential helpers, clone/smudge/pull filter invocation, and test binaries in `$BINPATH`.

Risks/test signals: failures are high severity because they imply current-directory command execution. The tests are platform-sensitive and carry comments documenting Go 1.19 `execerrdot` behavior to avoid false failures during setup.
