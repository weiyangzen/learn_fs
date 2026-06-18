<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdConfig.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdConfig.hh

Purpose: declares `XrdConfig`, the configuration/startup orchestrator for the Xrd server.

Important APIs/types/functions: public `Configure(int,char**)`, `ConfigXeq(char*,XrdOucStream&,XrdSysError*)`, constructor, `ProtInfo`, `NetADM`, and `NetTCP`. Private helpers and directive parsers match the implementation in `XrdConfig.cc`. State fields track identity, paths, TLS files/options, reporting, protocol list, network options, ports, permissions, strict fd handling, and max file descriptors.

Control flow: the public API gives callers one main startup entry point and a directive execution function used by config processing and dynamic updates. Private methods separate command parsing, config processing, network acquisition, TLS setup, protocol setup, pid/manifest work, and directive-specific parsing.

State and persistence behavior: the class stores all mutable startup configuration before it is committed to global runtime objects, filesystem paths, sockets, environment variables, and protocol configuration. `ProtInfo` is the handoff structure consumed by protocol loaders.

Dependencies: includes `XrdProtLoad.hh` and `XrdProtocol.hh`, uses `std::vector`, system types, and forward declarations for logging, networking, security, stream, monitor, and protocol helper types.

Integration points: instantiated by the server main path; owns `NetTCP` vector of bound networks; feeds `XrdProtLoad` and protocol plugins; coordinates with global log/scheduler/buffer/TLS state through implementation.

Risks: many private fields are raw pointers with ownership managed manually in implementation. Adding directives requires updating both header declaration and `ConfigXeq()` dispatch. Public `ProtInfo` and `NetTCP` expose mutable startup/runtime objects to consumers, so invariants are convention-based.

Test signals: compile tests when adding directive helpers; startup tests through `Configure()`; dynamic directive tests through `ConfigXeq()`; static analysis for pointer ownership and uninitialized fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdConfig.hh -->
