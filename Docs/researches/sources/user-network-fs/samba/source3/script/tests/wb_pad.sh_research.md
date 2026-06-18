# sources/user-network-fs/samba/source3/script/tests/wb_pad.sh

Purpose: build-time ABI check that `struct winbindd_request` and `struct winbindd_response` have identical sizes in 32-bit and 64-bit builds.

Important functions and APIs: dynamically writes a small C program including `nsswitch/winbind_client.h`, compiles it with `${CC:-gcc} -m32` and `-m64`, runs each binary with `req` and `resp`, and compares printed `sizeof` values. `cleanup()` removes generated sources/binaries and the temp directory.

Control flow: create `/tmp/wb_padXXXXXX`, generate C source, compile 32-bit and 64-bit binaries, run them to collect request/response sizes, cleanup, then fail if either pair differs.

State and persistence: creates temporary files under `/tmp` and removes them on normal paths, including compile failures.

Dependencies and integration: requires a compiler with both 32-bit and 64-bit support, Samba headers in the relative include paths, and any caller-provided `RPM_OPT_FLAGS`/`CFLAGS`. It is a low-level compatibility test for winbind client protocol structs.

Risks and test signals: many modern systems lack 32-bit build support, causing environment failures unrelated to Samba ABI. Passing signal is exact size equality for both request and response structures.
