## sources/user-network-fs/nfs-ganesha/src/Protocols/CMakeLists.txt

Purpose: top-level protocol subdirectory selector.

APIs and flow: always adds `NFS` and `XDR`, conditionally adds `NLM`, `RQUOTA`, `NFSACL`, and `9P` based on CMake options such as `USE_NLM`, `USE_RQUOTA`, `USE_NFSACL3`, and `USE_9P`.

State/dependencies: build configuration controls which protocol object libraries are available to the final server. No runtime state.

Risks/tests: option mismatches can leave descriptor tables compiled for protocols whose implementation objects are absent, or vice versa. Test all supported protocol option combinations, especially `USE_9P` and `USE_NFS3` interactions.
