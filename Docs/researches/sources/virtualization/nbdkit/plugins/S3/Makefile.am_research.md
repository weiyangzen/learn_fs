# File Research: sources/virtualization/nbdkit/plugins/S3/Makefile.am

This Automake file packages the Python `S3` plugin. `S3.py` is the source, and `nbdkit.py` is distributed as a test stub. When `HAVE_PYTHON` is true, it generates an executable script named `nbdkit-S3-plugin` by replacing `@sbindir@` in `S3.py`, then installs it as a plugin script with mode `0555`.

The file distributes `nbdkit-S3-plugin.pod` and conditionally builds the section 1 man page plus HTML documentation using `podwrapper.pl`.

No C module is compiled here; runtime dependencies are Python, boto3/botocore, and nbdkit's Python plugin loader.
