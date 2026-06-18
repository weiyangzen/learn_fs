# sources/test-tools/strace/src/kernel_dirent.h

Purpose: defines kernel `getdents` and `getdents64` directory-entry layouts for tracee buffer decoding.

Important APIs/types/functions: `kernel_dirent_t`, `kernel_dirent64_t`, `kernel_ulong_t`, `uint64_t`, `d_ino`, `d_off`, `d_reclen`, `d_type`, and flexible trailing `d_name[1]`.

Control flow: header-only type definitions; consumers iterate variable-length records using `d_reclen` and decode names from the trailing byte array.

State and persistence behavior: no state. Types model tracee buffer records rather than persisted data.

Dependencies and integration points: includes `kernel_types.h`; used by directory-entry syscall decoders where libc `struct dirent` cannot be trusted to match kernel ABI.

Risks: `kernel_dirent_t` uses tracee-sized long fields while `kernel_dirent64_t` fixes inode/offset to 64 bits. Incorrect record sizing can desynchronize directory-buffer iteration.

Test signals: `getdents`/`getdents64` tests should cover multiple records, unknown `d_type`, compat word sizes, and malformed/truncated record lengths.
