
# sources/user-network-fs/samba/source4/torture/man/smbtorture.1.xml

## Purpose
This DocBook XML file is the `smbtorture(1)` manual page for Samba 4.0. It documents the command used to run SMB, RPC, NBT, benchmark, and other torture tests against SMB servers. The page is not executable code, but it is an integration contract for users and automated documentation generation: it defines the expected command synopsis, accepted binding/UNC formats, common command-line options, and the operational warning around dangerous tests.

## Important APIs, Types, And Functions
The artifact uses the DocBook `refentry` schema rather than C APIs. Important elements are `refmeta`, `refnamediv`, `refsynopsisdiv`, `cmdsynopsis`, `arg`, `refsect1`, `refsect2`, `variablelist`, and `varlistentry`. The page exposes CLI options such as `-d`, `-U`, `-k`, `-W`, `-n`, `-O`, `-m`, `-s`, `-L`, `-X`, `-t`, `-p`, `-c`, `-A`, `-C`, `-N`, `-e`, and `-f`. It also documents positional arguments for a UNC/binding string and one or more test names.

## Control Flow
The document is organized in the standard manpage flow: metadata, name/purpose, synopsis, description, binding string format, UNC format, option list, version, related material, and authorship. The binding-string section describes how transports such as `ncacn_np`, `ncacn_ip_tcp`, and `ncalrpc` select SMB named pipes, RPC/TCP endpoints, or local RPC, with flags controlling signing, sealing, validation, packet printing, endian behavior, and pad checking.

## State And Persistence
This file persists no runtime state. It does, however, persist user-visible assumptions about `smbtorture`: default NBENCH time limit, option names, dangerous-test behavior, and the version target. Documentation drift here can create user-facing misconfiguration even when the binary works correctly.

## Dependencies
The file depends on the DocBook XML 4.2 DTD and Samba's manpage build pipeline. Semantically it depends on the `smbtorture` command-line parser and test registration surface matching the described options.

## Integration Points
The generated manual integrates with packaging, installed manpages, online docs, and operator workflows. The binding examples are especially tied to Samba's DCE/RPC binding parser and named-pipe routing. The NBENCH options connect to the nbench sources in this same subset.

## Risks
The synopsis appears to combine older `//server/share` usage with newer `BINDING-STRING|UNC TEST...` usage, so readers may need implementation help to know which options apply to each test class. The page names Samba 4.0 and can become stale as protocols, options, or supported dialects evolve. The `-X` option explicitly enables tests that may crash target servers, so this manual page has operational safety significance.

## Test Signals
Useful signals are documentation build success, DocBook validation, generated `smbtorture.1` readability, and spot-checks that documented options are still accepted by `smbtorture --help`. Test coverage should also compare described benchmark options such as `-t`, `-c`, and `-N` with the nbench implementation.
