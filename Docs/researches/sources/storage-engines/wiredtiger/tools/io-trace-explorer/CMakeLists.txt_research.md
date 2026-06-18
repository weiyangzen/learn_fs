# sources/storage-engines/wiredtiger/tools/io-trace-explorer/CMakeLists.txt

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/CMakeLists.txt

### Purpose
This CMake file builds the GTKmm-based `IOTraceExplorer` GUI for visualizing block-device and WiredTiger I/O traces.

### Important APIs, Types, and Functions
The project requires CMake 3.0, defaults to `RelWithDebInfo`, sets C++17, and creates an executable from `io_trace.cpp`, `main.cpp`, `main_window.cpp`, and `plot.cpp`. GTKmm dependencies are resolved either through `pkg-config` for `gtkmm-4.0` or through individual `find_library`/`find_path` calls when `VCPKG_TOOLCHAIN` is set.

### Control Flow
Configuration first chooses build type, then dependency strategy, then platform GUI options: `WIN32` with `mainCRTStartup` on MSVC and `MACOSX_BUNDLE` on Apple. Link libraries are registered globally before the executable target is declared.

### State and Persistence
Build artifacts are emitted into the CMake build tree only. No runtime state is created by this file.

### Dependencies and Integration Points
The build expects GTKmm 4 and its transitive C++ bindings for ATK, Cairo, GDK, GIO, GLib, Pango, and libsigc++. The target integrates the local parser, application, window, and plotting modules into one executable.

### Risks and Test Signals
The `VCPKG_TOOLCHAIN` branch uses broad `find_library` names and global `link_libraries`, so library names may not match all package managers. `add_cmake_flag` appears in the MSVC branch but is not a standard CMake command unless provided elsewhere, making that branch suspect. Build tests should configure both pkg-config and vcpkg paths where supported and compile with GTKmm 4 headers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/CMakeLists.txt -->
