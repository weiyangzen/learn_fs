# sources/user-network-fs/mergerfs/vendored/boost/config/platform/vxworks.hpp

Purpose: provides a deep Boost platform adaptation for VxWorks 6.9/7 and later-supported environments.

Important APIs/macros: validates `_WRS_VXWORKS_MAJOR >= 6`, defines `BOOST_PLATFORM "vxWorks"`, enables common headers and functions, pthreads, timers, `BOOST_LOCALE_WITH_ICU`, and ASIO serial/stream descriptor behavior. It corrects old VxWorks integer constant macros, declares or implements missing functions such as `getrlimit`, `setrlimit`, `truncate`, `symlink`, `readlink`, `gettimeofday`, `times`, `lstat`, and compatibility macros like `S_ISSOCK`, `FPE_FLTINV`, and `locale_t`. It disables many C++11 headers/features unless VxWorks 7 C++11 library configuration macros are present.

Control flow/dependencies: includes VxWorks headers (`version.h`, `<cstdint>`, `<sys/time.h>`, `<ioLib.h>`, `<tickLib.h>`, `<signal.h>` and others conditionally), defines inline C/C++ shim functions, then includes POSIX feature detection and cleans up misleading macros.

State and persistence: mostly compile-time macros, plus inline compatibility functions with no persisted state.

Integration points: selected by `__VXWORKS__`; affects Boost.Locale, Asio, Chrono, filesystem-like code, threading, and standard-library feature gates.

Risks and test signals: high risk because it declares replacement APIs and changes system macros. Test RTP versus DKM, VxWorks 6 versus 7, symlink/readlink failure semantics, truncate/gettimeofday/times shims, pthread priority inheritance notes, integer constants, and C++11 library configuration modes.
