# sources/user-network-fs/libsmb2/examples/CMakeLists.txt

Purpose: This CMake file builds a curated set of libsmb2 example executables when `ENABLE_EXAMPLES` is on.

Important APIs and types: It appends `${POPT_LIBRARY}` to `CORE_LIBRARIES`, defines a `SOURCES` list of executable basenames, loops with `foreach`, calls `add_executable`, `target_link_libraries`, `add_dependencies`, and adds `-Werror` plus `_U_=__attribute__((unused))`.

Control flow: Each source basename becomes an executable from `<name>.c`, links against `smb2` and `CORE_LIBRARIES`, and depends on the `smb2` target.

State and persistence behavior: Build outputs are example binaries in the CMake build tree. No files are installed here.

Dependencies and integration points: It depends on the root build having defined `smb2`, include directories, `CORE_LIBRARIES`, and potentially `POPT_LIBRARY`. The examples exercise public sync, async, raw, DCE/RPC, notify, and server APIs.

Risks: The CMake examples list differs from `examples/Makefile.am`; CMake omits some autotools examples such as `smb2-ls-epoll`, share enum sync, stat/statvfs/truncate/rename. `POPT_LIBRARY` is appended without local discovery in this file.

Test signals: Configure with `-DENABLE_EXAMPLES=ON` and verify each listed executable compiles and links. Comparing CMake and autotools example lists helps catch accidental coverage drift.
