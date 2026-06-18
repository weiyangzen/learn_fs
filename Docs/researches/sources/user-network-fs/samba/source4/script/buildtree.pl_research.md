<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/buildtree.pl -->
# sources/user-network-fs/samba/source4/script/buildtree.pl

## Purpose

`buildtree.pl` mirrors the source directory tree into the build directory by creating corresponding directories while excluding paths under the build directory itself.

## Important APIs, Types, and Functions

It uses Perl `File::Find`, `File::Path::mkpath`, and `Cwd::abs_path`. Environment variables `builddir` and `srcdir` supply roots. The `wanted()` callback handles each filesystem entry.

## Control Flow

The script resolves absolute source/build roots, walks `$srcdir`, and for every directory not inside `$builddir`, substitutes the source prefix with the build prefix, creates the destination directory, and prints the created path.

## State and Persistence Behavior

It persists directory creation in the build tree. It does not copy file contents or remove old directories.

## Dependencies and Integration Points

It is a build helper used by source4 build processes that require a build tree shaped like the source tree.

## Risks and Edge Cases

Regex substitution on paths can behave oddly if source/build paths contain regex metacharacters. Missing `builddir` or `srcdir` environment variables cause `abs_path()` problems. Symlink and permission behavior follows `File::Find` and `mkpath`.

## Test Signals

Tests should run it with temporary source/build trees, nested directories, a build directory inside the source, and missing environment variables.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/buildtree.pl -->
