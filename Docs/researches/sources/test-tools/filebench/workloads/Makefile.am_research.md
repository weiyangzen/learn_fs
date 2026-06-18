# `sources/test-tools/filebench/workloads/Makefile.am`

Purpose: Automake manifest for installing Filebench workload model files.

Important APIs and build variables: `workloadsdir = @datadir@/filebench/workloads` selects the install location. `workloads_DATA` enumerates `.f` workload definitions such as filemicro, fileserver, oltp, webserver, varmail, videoserver, and stream workloads. `EXTRA_DIST = $(workloads_DATA)` ensures the same workload files are included in distribution tarballs.

Control flow: During `make install`, Automake installs every file listed in `workloads_DATA` into the configured data directory. During distribution packaging, `EXTRA_DIST` includes the workload files even though they are data rather than compiled sources.

State and persistence: No runtime state. The persistent effect is installation of workload model assets used by Filebench users and tests.

Dependencies and integration: Depends on Automake conventions and the presence of every listed `.f` file in the workloads directory. Integrated with the Filebench build and release packaging system.

Risks and test signals: Missing listed workload files break `make dist` or install. New workload files are not installed unless added here. Tests should run `make distcheck` or equivalent packaging checks and verify installed workload paths.
