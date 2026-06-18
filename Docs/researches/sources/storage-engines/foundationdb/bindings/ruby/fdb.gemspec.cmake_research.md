# sources/storage-engines/foundationdb/bindings/ruby/fdb.gemspec.cmake

Purpose: This is the CMake-configured Ruby gemspec template used during build packaging.

Important APIs and types: It defines `Gem::Specification` fields including name `fdb`, version `${FDB_VERSION}`, current date, summary/description, authors/email, file list, homepage, Apache-2.0 license, dependency on `ffi`, Ruby version `>= 1.9.3`, and a client-library requirement note.

Control flow: CMake substitutes `${FDB_VERSION}` and writes `fdb.gemspec`; RubyGems then reads it during `gem build`.

State and persistence behavior: It affects gem metadata and packaged file list, not runtime behavior.

Dependencies and integration points: It must match `CMakeLists.txt` source copying and Ruby library `require_relative` paths. It depends on RubyGems and the `ffi` gem.

Risks: The file list must be updated when Ruby binding files change. The broad `ffi` version range reflects legacy support and may need review for newer Ruby/platform combinations.

Test signals: `gem build fdb.gemspec` should include all runtime files and expose the substituted FoundationDB version.
