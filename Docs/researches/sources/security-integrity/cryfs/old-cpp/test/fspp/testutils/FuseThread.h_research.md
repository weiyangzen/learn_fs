# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseThread.h

Purpose: declares the non-copyable helper for running a FUSE instance in a background test thread.

Important APIs/types: `FuseThread(fspp::fuse::Fuse*)`, `start(const boost::filesystem::path&, const std::vector<std::string>&)`, and `stop()`.

Control flow/state: the header defines ownership boundaries: `FuseThread` does not own `_fuse`, but it owns `_child`. Copy and assignment are disabled through cpp-utils macros to avoid double-stop or thread ownership mistakes.

Dependencies/integration: Boost thread/chrono/path, cpp-utils macros, and a forward declaration of `fspp::fuse::Fuse`.

Risks: because the `Fuse*` is raw and non-owning, callers must preserve object lifetime. The class has no destructor, so users must call `stop()` explicitly or embed it in an RAII owner such as `TempTestFS`.

Test signals: no standalone tests; correctness is visible through FUSE test fixture startup/shutdown stability.
