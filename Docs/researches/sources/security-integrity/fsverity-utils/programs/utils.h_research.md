# sources/security-integrity/fsverity-utils/programs/utils.h

Purpose: This header declares utility functions and resource wrappers shared by fsverity CLI command implementations.

Important APIs and types: It exposes `struct filedes`, allocation helpers, error printers, full I/O functions, file sizing, hex helpers, and tree-parameter parsing used by digest/sign/enable commands.

Control flow and state: No executable flow exists, but the header standardizes ownership and cleanup expectations for opened file descriptors and allocated buffers.

Dependencies and integration points: Included by command and test sources. It must remain consistent with `programs/utils.c`.

Risks and test signals: Header/implementation mismatch causes compile failures or subtle ABI issues within the program. Signals include all subcommands building and shared helper behavior covered through command tests.
