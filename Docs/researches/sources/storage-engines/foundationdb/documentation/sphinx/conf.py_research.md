# sources/storage-engines/foundationdb/documentation/sphinx/conf.py

## Purpose
This is the Sphinx configuration for FoundationDB documentation. It configures extensions, theme, version metadata, HTML/LaTeX/man/Texinfo outputs, and enforces explicit roles by making the default role intentionally fail.

## Important APIs, Types, And Functions
The `extensions` list enables Sphinx built-ins plus local `brokenrole`, `relativelink`, and `rubydomain`. `sys.path.insert` exposes the local `extensions` directory. Version metadata is loaded from a `versions.target` XML file near the Python executable when present; otherwise CMake supplies `version` and `release` via `-D`. HTML uses `sphinx_bootstrap_theme` with local TOC sidebars and disabled Sphinx footer/source index features. `default_role = "broken"` routes unqualified backtick roles to the custom error role.

## Control Flow
At Sphinx startup, the module imports theme support, adds extension paths, optionally parses MSBuild XML version data, and assigns Sphinx config variables. No functions are defined here beyond configuration-time logic.

## State And Persistence
There is no runtime persistence. Sphinx consumes the config to create generated HTML, LaTeX, man, and Texinfo outputs in the build tree.

## Dependencies And Integration Points
Dependencies include `sphinx_bootstrap_theme`, Sphinx, local extensions, and optional `versions.target` XML. It integrates with `documentation/CMakeLists.txt`, which passes version/release overrides and points Sphinx at this config with `-c`.

## Risks
The computed `version_path` depends on `sys.executable`, which can differ between system Python, virtualenv Python, and packaged contexts. Copyright year and theme dependencies can drift. Setting `default_role` to a deliberately failing role is useful for docs hygiene but makes casual reST shorthand a hard build error under the CMake `-W` policy.

## Test Signals
Signals include successful `sphinx-build -W -b html`, correct rendered version/release strings, proper bootstrap theme rendering, and intentional failure when a document uses an unqualified default role.
