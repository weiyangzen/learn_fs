# sources/distributed-fs/xrootd/src/XrdSecztn/CMakeLists.txt

Purpose: build description for the ZTN security plugin.

Important targets: sets `XrdSecztn` to `XrdSecztn-${PLUGIN_VERSION}`, builds a module from `XrdSecProtocolztn.cc` and `XrdSecztn.cc`, links privately to `XrdUtils`, and installs the module library.

Control flow: no conditionals or aggregate dependency line in this file; it assumes the parent build includes and installs the module target.

State and persistence: no runtime state. It only controls build/install metadata for the ZTN plugin.

Dependencies and integration: uses repository plugin-version conventions and CMake install lib dir. The implementation files are outside this work item but are the runtime integration points.

Risks: unlike the SSS and Unix CMake files, this one does not call `add_dependencies(plugins ${XrdSecztn})`; if the parent expects that aggregate dependency, ZTN may be omitted from plugin umbrella builds.

Test signals: configure/build, verify the module is produced and installed, and compare plugin aggregate behavior with other security modules.
