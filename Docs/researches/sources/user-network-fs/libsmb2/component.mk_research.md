# sources/user-network-fs/libsmb2/component.mk

Purpose: This file describes libsmb2 as an ESP-IDF component for legacy Make-based ESP-IDF builds.

Important APIs and types: It sets `COMPONENT_SRCDIRS=lib`, `COMPONENT_PRIV_INCLUDEDIRS=lib include/esp`, and `COMPONENT_ADD_INCLUDEDIRS=include include/smb2`.

Control flow: ESP-IDF's build system reads these variables to compile sources under `lib`, expose public include directories, and include private implementation headers for the component.

State and persistence behavior: There is no state in this file; it influences generated ESP-IDF build artifacts.

Dependencies and integration points: It complements the ESP branch in `CMakeLists.txt`, `idf_component.yml`, and ESP-specific headers under `include/esp`.

Risks: Only `lib` is listed as a source directory, so new source directories must be reflected here for legacy ESP builds. Private/public include separation must stay aligned with ESP-IDF expectations.

Test signals: Build an ESP-IDF project that depends on libsmb2 and verify public headers resolve while private includes remain available to component sources.
