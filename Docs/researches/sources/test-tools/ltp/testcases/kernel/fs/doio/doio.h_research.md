# sources/test-tools/ltp/testcases/kernel/fs/doio/doio.h

Purpose: `doio.h` defines the binary protocol consumed by `doio.c` and produced by companion I/O generators. It assigns numeric request IDs for legacy, platform-specific, and POSIX-like I/O operations and defines the packed request structures that are read directly from an input stream.

Important APIs and types: the header exports request type constants such as `READ`, `WRITE`, `READA`, `WRITEA`, `LISTIO`, listio variants, `PREAD`, `PWRITE`, `READV`, `WRITEV`, `AREAD`, `AWRITE`, `MMAPR`, `MMAPW`, `RESVSP`, `UNRESVSP`, `FSYNC2`, `FDATASYNC`, and `BIOSIZE`. It defines `DOIO_MAGIC`, user flag `F_WORD_ALIGNED`, exit-status bits `E_NORMAL` through `E_SIGNAL`, async completion strategies `A_POLL` through `A_CALLBACK`, `MAX_FNAME_LENGTH`, and the request structs `read_req`, `write_req`, `ssread_req`, `sswrite_req`, `listio_req`, and `io_req`.

Control flow role: the header has no runtime control flow, but its field layout drives the executor. `doio.c` relies on `r_file`, `r_oflags`, `r_offset`, and `r_nbytes` occupying matching positions in the read/write/list-compatible structures, and `r_pattern` matching between write-shaped requests. `struct io_req` wraps a `r_type`, `r_magic`, and union so the executor can switch by type while sharing field access through `r_data.io`.

State and persistence behavior: requests are intended to be serialized as raw C structs, so the ABI is persistent across producer and consumer processes rather than across heterogeneous machines. `r_magic` is the only embedded validation marker. File names are stored inline with a fixed 128-byte maximum, and offsets/counts are `int`, making the request format compact but not fully large-file neutral.

Dependencies and integration points: every tool that generates or consumes doio work must include or faithfully mirror this header. It integrates directly with `doio.c` dispatch tables and indirectly with write-log and corruption-checking tools through shared assumptions about file paths, offsets, lengths, and write patterns.

Risks: raw struct serialization is sensitive to compiler ABI, endian, padding, and field-size differences. The header has no include guard in the displayed source, so multiple inclusion relies on build discipline. Some constants are for CRAY/IRIX-only system calls and may be unsupported on modern Linux. The comment notes a critical layout invariant; changing any request field order can silently corrupt execution.

Test signals: useful validation is cross-tool round-trip generation of `struct io_req`, rejection of bad `DOIO_MAGIC`, and successful dispatch of each request type supported by the target build. Compile failures or request-size mismatches are strong indicators that producer and consumer are no longer ABI-compatible.
