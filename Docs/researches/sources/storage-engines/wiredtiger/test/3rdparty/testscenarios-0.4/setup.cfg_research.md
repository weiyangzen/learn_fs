# sources/storage-engines/wiredtiger/test/3rdparty/testscenarios-0.4/setup.cfg

Purpose: setuptools egg-info configuration for the vendored `testscenarios` release.

Important APIs, types, and functions: `[egg_info]` sets `tag_build` empty, `tag_date = 0`, and `tag_svn_revision = 0`.

Control flow: setuptools reads this during egg-info and distribution metadata generation to avoid date and revision suffixes in generated package metadata.

State and persistence: no runtime state. Packaging commands persist generated egg-info according to these options.

Dependencies and integration points: integrates with `setup.py` and legacy setuptools/distutils metadata generation.

Risks and test signals: low risk; stale legacy fields reflect older packaging practices. Test signal is stable package version metadata without automatic build/date suffixes.
