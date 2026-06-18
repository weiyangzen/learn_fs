## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/constants.py

Purpose: command-name constants for blockade network tests.

Important APIs/types/functions: `Command` class exposes string constants `docker`, `docker_compose`, `ozone`, and `freon`. `ozone` points at `/opt/hadoop/bin/ozone`; `freon` is `/opt/hadoop/bin/ozone freon`.

Control flow: there is no executable flow; other modules import constants to build docker and Ozone commands.

State and persistence behavior: no state. The values represent external command entry points inside the test environment.

Dependencies and integration points: imported by `ozone.util`, `ozone.cluster`, and `ozone.client`.

Risks: command paths are hard-coded for the Ozone docker image. Changing the image layout or docker-compose binary name requires updating this file. `freon` embeds a space, so callers must know whether a list item is a shell fragment rather than an argv token.

Test signals: failures show up as command-not-found or nonzero exit assertions in blockade tests.
