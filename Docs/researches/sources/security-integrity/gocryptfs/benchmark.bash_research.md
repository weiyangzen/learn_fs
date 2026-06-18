# sources/security-integrity/gocryptfs/benchmark.bash

Purpose: This benchmark runner measures canonical gocryptfs performance scenarios, optionally comparing EncFS, loopback, OpenSSL on/off, dd-only modes, and XChaCha variants.

Important APIs and steps: It parses options, prepares temporary directories, initializes encrypted filesystems, mounts with selected flags, runs file creation/copy/read/write benchmarks, and prints comparable results.

Control flow and state: Option parsing controls benchmark modes. The script creates mount/cipher/plain paths, invokes external tools, and must unmount and clean up at exit.

Dependencies and integration points: Depends on the local `gocryptfs` binary, optional EncFS, FUSE support, dd/coreutils, and project comparison documentation.

Risks and test signals: Results are hardware/cache sensitive and not unit-test stable. Main signals are successful command execution, no leftover mounts, and sane option validation.
