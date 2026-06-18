# sources/security-integrity/gocryptfs/benchmark-reverse.bash

Purpose: This script benchmarks gocryptfs reverse mode, where a plaintext tree is exposed as an encrypted view.

Important APIs and steps: It sets up temporary directories, initializes or mounts reverse-mode filesystems, runs throughput or filesystem operation benchmarks, and records timings for comparison.

Control flow and state: The script creates temporary plaintext/cipher/mount paths, runs commands, unmounts, and cleans up. State is benchmark data and temporary filesystem contents.

Dependencies and integration points: Integrates the built `gocryptfs` binary, FUSE unmount helpers, shell tools, and benchmark documentation.

Risks and test signals: Benchmarks are environment-sensitive and can leave mounts behind on failure. Signals are successful mount/unmount, repeatable benchmark phases, and cleanup of temporary mounts.
