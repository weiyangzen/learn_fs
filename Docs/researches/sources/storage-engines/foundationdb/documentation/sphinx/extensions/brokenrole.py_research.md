# sources/storage-engines/foundationdb/documentation/sphinx/extensions/brokenrole.py

## Purpose
This Sphinx extension defines a role named `broken` that always emits an error. `conf.py` sets it as the default role to catch accidental single-backtick markup that lacks an explicit semantic role.

## Important APIs, Types, And Functions
`setup(app)` registers the role with `app.add_role("broken", broken_role)`. `broken_role` builds a reporter error with message `Broken role invoked`, wraps the raw text as a problematic node, and returns both the node and system message.

## Control Flow
Sphinx/docutils invokes `broken_role` whenever the `broken` role is used. Since it is the default role, unqualified interpreted text triggers this path.

## State And Persistence
No state is stored. Effects are limited to the current Sphinx parse/build.

## Dependencies And Integration Points
It depends on the docutils role callback contract supplied through Sphinx. It is loaded by `conf.py` and works with `-W` in the CMake docs build to turn these errors into build failures.

## Risks
This extension intentionally breaks builds for default-role usage; that is desired for markup discipline but can surprise documentation contributors. It does not return extension metadata such as version or parallel-read safety.

## Test Signals
A minimal reST document containing unqualified `` `text` `` should produce a Sphinx error, while explicit roles should not invoke this extension.
