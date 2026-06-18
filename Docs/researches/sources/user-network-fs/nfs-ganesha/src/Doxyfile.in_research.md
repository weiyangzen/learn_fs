<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Doxyfile.in -->
# sources/user-network-fs/nfs-ganesha/src/Doxyfile.in

Purpose: Doxygen configuration template used by the top-level CMake `doc` target to generate NFS-Ganesha API/source documentation. CMake substitutes source and build paths before invoking Doxygen.

Important APIs, types, and functions: Key project settings are `PROJECT_NAME = "NFS-Ganesha"`, `PROJECT_BRIEF = "An NFS server in userspace"`, `OUTPUT_DIRECTORY = doc/doxygen`, `OPTIMIZE_OUTPUT_FOR_C = YES`, `TYPEDEF_HIDES_STRUCT = YES`, and `EXTENSION_MAPPING = h=C`. Input is `@CMAKE_CURRENT_SOURCE_DIR@`, recursion is enabled, and excludes remove tools, tests, scripts, packaging, samples, `FSAL_GPFS`, `FSAL_GLUSTER`, and `libntirpc`. Output settings enable HTML and LaTeX, disable man/XML/RTF, and leave source browser off. Warning settings enable documentation warnings but do not warn for undocumented members.

Control flow: During configure, `CMakeLists.txt` runs `configure_file(... @ONLY)` to create a concrete `Doxyfile` in the build directory. The `doc` custom target then runs `${DOXYGEN_EXECUTABLE}` against that file from the build directory. Doxygen recursively scans the configured source tree, applies excludes and preprocessing rules, emits HTML under `doc/doxygen/html`, and emits LaTeX under `doc/doxygen/latex`.

State and persistence behavior: The template itself is static. Generated documentation persists in the build tree under `doc/doxygen`. `HTML_TIMESTAMP = YES` means outputs include generation times and are not stable for byte-for-byte reproducibility unless changed. `WARN_LOGFILE` is empty, so warnings go to stderr rather than a persisted log.

Dependencies and integration points: Depends on Doxygen, optionally LaTeX tools for full LaTeX/PDF output, and optionally Graphviz if `HAVE_DOT` is changed from the current `NO`. It is only used if `find_package(Doxygen)` succeeds in the root build. The include/exclude choices shape which FSALs and subsystems appear in developer docs; Ceph FSAL is included, while GPFS and Gluster are explicitly excluded.

Risks: `PROJECT_NUMBER = pre-2.0` appears stale relative to the top-level Ganesha version and can mislabel generated docs. `EXTRACT_ALL = NO`, `EXTRACT_STATIC = NO`, no macro expansion, and source browser disabled mean much internal code and static functions may be absent even when relevant. The exclusion list may hide useful tests or FSAL implementations from API documentation. Enabling LaTeX by default can make the doc target heavier or fail later on hosts without a full TeX stack.

Test signals: Configure with Doxygen installed and run the `doc` target. Healthy output should include generated HTML for documented C APIs, warnings limited to expected doc issues, no path substitution literals left as `@CMAKE_CURRENT_SOURCE_DIR@`, and no accidental inclusion of excluded subtrees.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Doxyfile.in -->
