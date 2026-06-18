# sources/security-integrity/ima-evm-utils/autogen.sh

## Purpose
Minimal bootstrap script for generating Autotools build files.

## Important APIs, Types, And Functions
- `set -e` exits on bootstrap failure.
- `autoreconf -i` installs missing helper files and regenerates configure machinery.

## Control Flow
The script simply invokes `autoreconf -i` from the caller's current checkout context.

## State And Persistence
Writes generated Autoconf/Automake/Libtool files such as `configure`, `Makefile.in`, `aclocal.m4`, and helper scripts.

## Dependencies And Integration Points
Depends on autoconf, automake, libtool, and m4 macro availability.

## Risks And Edge Cases
It does not enforce running from the repository root; callers normally invoke it from `build.sh` after `cd dirname $0`.

## Test Signals
Success is a generated `configure` script usable by the subsequent build.
