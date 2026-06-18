<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/Distribution.xml -->
# Research: sources/storage-engines/foundationdb/packaging/osx/Distribution.xml

## Purpose
macOS productbuild distribution manifest for the combined FoundationDB installer UI.

## Important APIs, Types, And Functions
Defines package refs, background/title, minimum macOS version, root-volume install options, choices for clients and server, dependencies making server selectable only with clients, and conclusion resource.

## Control Flow
Productbuild reads this XML and composes `FoundationDB-clients.pkg` and `FoundationDB-server.pkg` into a user-customizable installer.

## State And Persistence Behavior
No runtime state itself; it controls which pkg payloads and scripts will run.

## Dependencies And Integration Points
Depends on `productbuild`, the two component packages, resource files, and `buildpkg.sh` which injects `hostArchitectures` with `sed`. This is the macOS installer front-end contract.

## Risks And Edge Cases
The build script mutates this source file in place to add host architecture, creating potential dirty-tree/stale XML risk. Minimum OS and choice dependencies are static and may drift.

## Test Signals
Validated by successful `productbuild` and interactive/silent install tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/Distribution.xml -->
