# sources/distributed-fs/xrootd/src/XrdVoms/CMakeLists.txt

Purpose: Conditionally builds and installs the VOMS plugin module.

Important APIs/types/functions: Clears BUILD_VOMS cache, returns unless ENABLE_VOMS, uses find_package(VOMS) or REQUIRED when FORCE_ENABLED, sets BUILD_VOMS on success, creates plugin target XrdVoms-${PLUGIN_VERSION}, and symlinks libXrdHttpVOMS-${PLUGIN_VERSION}.so and libXrdSecgsiVOMS-${PLUGIN_VERSION}.so to the same module.

Control flow: If VOMS is disabled or unavailable, the whole directory contributes no target. When found, it compiles XrdVomsFun.cc, XrdVomsHttp.cc, XrdVomsMapfile.cc, and XrdVomsgsi.cc, links XrdUtils, VOMS libraries, and OpenSSL::SSL, and installs the module plus symlinks.

State/persistence: Build cache variable BUILD_VOMS records availability. Install-time symlinks persist in the install libdir.

Dependencies/integration: Integrates with external VOMS headers/libraries, XrdUtils, OpenSSL, and XRootD plugin naming/version scheme.

Risks: The install(CODE) symlink commands assume Unix-like ln and lib prefix/suffix. Both HTTP and SecGSI plugin entry points must live in the same shared object. If FORCE_ENABLED is set, missing VOMS is a hard configure failure.

Test signals: Configure with ENABLE_VOMS off/on, FORCE_ENABLED on with missing VOMS, build plugin, verify symlinks, and load both HTTP and GSI plugin symbols from the installed module.
