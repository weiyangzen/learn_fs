# sources/storage-engines/wiredtiger/tools/xray_to_optrack/CMakeLists.txt Research

## Purpose

This CMake file conditionally builds the `xray_to_optrack` utility, which converts LLVM XRay traces to WiredTiger OpTrack logs. It ensures the tool is only built when the compiler and LLVM libraries support the required XRay APIs.

## Important APIs, Types, and Functions

The script sets `cmake_minimum_required(VERSION 3.21)` and declares a CXX project. It checks `CMAKE_CXX_COMPILER_ID` for Clang or AppleClang, requires compiler version at least 8, configures CMake package sorting to prefer the newest LLVM package, calls `find_package(LLVM CONFIG REQUIRED)`, requires `LLVM_PACKAGE_VERSION >= 8`, maps LLVM components with `llvm_map_components_to_libnames(llvm_libs support core symbolize xray)`, and creates the executable from `xray_to_optrack.cpp`.

## Control Flow

Configuration returns early with a status message when the compiler is not Clang-like, the compiler is too old, or LLVM is too old. If all gates pass, it adds include directories, compile definitions, and target libraries from LLVM.

## State and Persistence Behavior

This file affects build-system configuration only. It creates the build target when dependencies are present and otherwise skips it without failing the whole WiredTiger build. It writes no runtime state.

## Dependencies and Integration Points

The parent WiredTiger CMake build includes this directory from `sources/storage-engines/wiredtiger/CMakeLists.txt`. The utility depends on LLVM Support, Core, Symbolize, and XRay components plus Clang-compatible XRay instrumentation support.

## Risks and Edge Cases

`find_package(LLVM CONFIG REQUIRED)` is reached only after compiler checks but remains required; a Clang build without LLVM CMake package files can fail configuration instead of silently skipping. The component list and LLVM APIs may shift across newer LLVM versions. Returning from a subdirectory CMake file is intentional but depends on being included with `add_subdirectory`.

## Test Signals

Build matrix coverage should include non-Clang compilers, Clang without LLVM package files, LLVM below 8, and a modern LLVM/Clang environment that successfully links `xray_to_optrack`.
