# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sarc4.c

Implements the Arcfour/RC4-compatible stream cipher filter. `s_arcfour_set_key` initializes the 256-byte S-box with the key scheduling algorithm, and `s_arcfour_process` generates the keystream while XORing input to output.

The same processing path encrypts and decrypts because Arcfour is XOR-stream based. State consists of the S-box and two indices, saved after each buffer chunk for resumable stream processing. `s_arcfour_process_buffer` provides an in-place buffer helper around the stream cursor API.

Dependencies include Ghostscript stream implementation headers and error conventions. It exports `s_arcfour_template`.

Security note: Arcfour/RC4 is legacy cryptography retained for PDF compatibility. This file is not filesystem code.
