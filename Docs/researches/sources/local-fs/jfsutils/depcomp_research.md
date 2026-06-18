# File Research: sources/local-fs/jfsutils/depcomp

This is Automake’s `depcomp` helper script, version `2009-04-28.21`. It wraps compiler invocations so dependency files are generated consistently across different compilers and platforms.

Primary behavior:
- Requires environment variables `depmode`, `source`, and `object`.
- Derives dependency output paths such as `.deps/<object>.Po` when `depfile` is not provided.
- Runs the compiler command passed as arguments.
- Converts compiler-specific dependency output into Makefile-compatible dependency files.
- Adds dummy dependency targets for headers to avoid build failures when headers are removed.
- Falls back to simply executing the compiler when `depmode=none`.

Supported dependency modes:
- `gcc3`: uses `-MT`, `-MD`, `-MP`, and `-MF`.
- `gcc`/`hp`: uses GCC-style `-M`/`-MD` preprocessor dependency output.
- `sgi`: supports IRIX compiler dependency output.
- `aix`: handles AIX compiler `.u` dependency files.
- `icc`: handles Intel compiler `-MD -MF` quirks.
- `hp2`: handles HP/aCC `+Maked` output.
- `tru64`: handles Tru64 compiler dependency side files.
- `dashmstdout` and `dashXmstdout`: parse compiler `-M`-style stdout output.
- `makedepend`: invokes external `makedepend`.
- `cpp`: extracts dependencies from preprocessor line markers.
- `msvisualcpp` and `msvcmsys`: handles Visual C++ preprocessor output.
- `none`: runs the compiler without dependency tracking.

Important integration points:
- `configure` tests this script to choose `CCDEPMODE`.
- Generated Makefiles include `.deps/*.Po` files that this script creates.
- The script is part of the distributed build machinery, not jfsutils domain logic.

Portability/build observations:
- This is generated/imported Automake infrastructure and should not usually be edited.
- It exists to support many legacy compiler environments that jfsutils itself may never actively target today.
- Build issues involving dependency tracking are usually better addressed by regenerating Automake files or configuring with `--disable-dependency-tracking`.
