# sources/security-integrity/fsverity-utils/programs/cmd_enable.c

Purpose: This CLI command enables fs-verity on a target file, optionally setting hash algorithm, block size, salt, and a detached signature.

Important APIs and functions: `read_signature()` loads a nonempty signature file with a maximum size guard. `fsverity_cmd_enable()` parses tree parameters and `--signature`, opens the target file read-only, and calls `libfsverity_enable_with_sig`.

Control flow and state: Parsed options populate `libfsverity_merkle_tree_params`; optional signature bytes are allocated then freed after ioctl. Successful execution persists kernel fs-verity state on the file.

Dependencies and integration points: Integrates CLI parsing, library enable wrapper, Linux ioctl UAPI, and signatures created by `cmd_sign`.

Risks and test signals: Risks include irreversible enablement, signature file size constraints, hash parameter mismatch with precomputed signatures, and filesystem/kernel support. Signals include ioctl success, proper errno diagnostics, and usage failures for duplicate or invalid options.
