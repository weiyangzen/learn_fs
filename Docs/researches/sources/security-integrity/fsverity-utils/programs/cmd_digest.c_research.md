# sources/security-integrity/fsverity-utils/programs/cmd_digest.c

Purpose: This CLI command computes and prints the fs-verity digest of a file, optionally using custom hash algorithm, block size, salt, compact output, and metadata side outputs.

Important APIs and functions: `fsverity_cmd_digest()` parses long options, opens the input file, fills `libfsverity_merkle_tree_params`, calls `libfsverity_compute_digest`, and prints hex digest information. It uses shared CLI parsing helpers for tree parameters and file I/O.

Control flow and state: Command state is option flags, opened file descriptor, allocated digest, and optional metadata callback context. It exits with usage status for invalid arguments and error status for I/O or digest failures.

Dependencies and integration points: Bridges the public library digest API with `programs/utils.c`, hash-alg parsing, and test programs.

Risks and test signals: Risks include salt parsing, output format stability, duplicate options, and file-size/read errors. Signals include command-line tests with known digest vectors and invalid-argument cases.
