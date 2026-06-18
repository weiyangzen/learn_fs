<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/packaging/RPM/makerpms.sh -->
# sources/user-network-fs/libsmb2/packaging/RPM/makerpms.sh

Purpose: Automates creation of source tarballs and RPM builds from a tagged libsmb2 git checkout.

Important APIs, types, and functions: Uses `git describe` to derive `VERSION`, rpm macro expansion for spec/source directories, optional gzip `--rsyncable`, generated spec substitution, tarball creation, and `rpmbuild` invocation.

Control flow: The script validates the tag prefix, maps exact tags to release versions and non-exact descriptions to `.devel` versions, stages sources/spec files into RPM directories, and runs the package build with optional extra configure arguments.

State and persistence behavior: Writes tarballs and spec files into the user's RPM build tree. It does not modify source files other than generated packaging outputs outside the checkout.

Dependencies and integration points: Depends on git tags, rpm/rpmbuild, tar/gzip, sed, and the RPM spec template. Intended for release engineering rather than normal library runtime.

Risks: Fails hard when not on a `libsmb2-*` describe result. Uses backticks and unquoted expansions in several places, so unusual paths may break. Reproducibility depends on local toolchain and RPM macro configuration.

Test signals: No direct test; successful RPM generation is the acceptance signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/packaging/RPM/makerpms.sh -->
