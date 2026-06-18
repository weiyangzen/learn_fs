# sources/storage-engines/foundationdb/cmake/DotnetImports.props.in

## Purpose
MSBuild property template used by dotnet-based C# tool builds.

## Important APIs, Types, and Functions
Defines `<OutDir>`, `<DOTNET_PACKAGE_VERSION>`, and injectable custom build props.

## Control Flow and Integration
`Finddotnet.cmake`/tooling can configure this file to route dotnet build outputs into a known directory and propagate package version metadata.

## State and Persistence
Depends on `_DN_OUTPUT_PATH`, `_DN_VERSION`, and `_DN_CUSTOM_BUILDPROPS` substitutions.

## Dependencies
Configured props files persist in the generated build tree; no runtime state.

## Risks and Test Signals
Risks are malformed XML from custom props or paths, and output directory mismatches. Test signal is successful dotnet project build using configured imports.
