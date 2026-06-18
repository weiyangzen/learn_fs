# File Research: sources/windows/winbtrfs/src/tests/manifest.xml

## Purpose

`manifest.xml` is the Windows application manifest for the WinBtrfs test executable. It declares OS compatibility, active code page behavior, and administrator privilege requirements for the `btrfs-test` binary.

## Manifest Contents

- Defines assembly identity `btrfs-test` with version `0.0.0.0`.
- Declares compatibility with Windows Vista, Windows 7, Windows 8, Windows 8.1, and Windows 10 using Microsoft `supportedOS` GUIDs.
- Sets the process `activeCodePage` to `UTF-8` through the `http://schemas.microsoft.com/SMI/2019/WindowsSettings` namespace.
- Requests `requireAdministrator` execution level with `uiAccess="false"`.

## Role in the Test Suite

The administrator requirement matches the test suite's use of privileged filesystem operations, token privilege manipulation, ACL changes, section/image mapping scenarios, and low-level NT APIs. The UTF-8 active code page setting is relevant because the tests exercise Unicode and UTF-8-sensitive filename behavior, especially in `links.cpp`.

## Dependencies and Cross-File Interactions

This file is consumed by the Windows build/link process for the test executable rather than by C++ source at runtime. It supports the assumptions made by the tests in `links.cpp` and `mmap.cpp`: the process is elevated, runs under known Windows compatibility behavior, and uses UTF-8 as its active code page.

## Research Summary

`manifest.xml` is a small but important runtime contract for the WinBtrfs test binary. It ensures elevated execution and UTF-8 process code page behavior, both of which affect the reliability of the hardlink, ACL, Unicode filename, and memory-mapping tests in this directory.
