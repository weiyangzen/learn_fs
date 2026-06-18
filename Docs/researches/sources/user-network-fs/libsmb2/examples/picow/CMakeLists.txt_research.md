# sources/user-network-fs/libsmb2/examples/picow/CMakeLists.txt

Purpose: This standalone CMake file demonstrates building libsmb2 and a directory-listing example for Raspberry Pi Pico W with FreeRTOS and lwIP.

Important APIs and types: It sets `PICO_SDK_PATH`, `FREERTOS_KERNEL_PATH`, `LIBSMB2_PATH`, Wi-Fi credentials, `SMB2_URL`, `PICO_BOARD=pico_w`, includes Pico SDK and FreeRTOS import scripts, calls `pico_sdk_init`, adds libsmb2 as a subdirectory, builds `smb2-ls-sync` from `main.cpp`, enables USB stdio, and links Pico, CYW43 lwIP FreeRTOS, FreeRTOS heap, and libsmb2 libraries.

Control flow: Users edit the configuration block, CMake initializes the embedded SDKs, libsmb2 is built with Pico-specific settings from the root CMake file, then the example executable is compiled and extra Pico output formats are generated.

State and persistence behavior: Build output includes Pico firmware artifacts, CMake cache values containing Wi-Fi/SMB URL strings, and generated config headers.

Dependencies and integration points: It integrates Pico SDK, FreeRTOS Kernel, lwIP, CYW43 Wi-Fi, libsmb2 includes, and `examples/picow/main.cpp`.

Risks: The file contains placeholder paths and credentials that must be edited locally. Wi-Fi password and SMB URL become compile definitions and can leak through build artifacts. The comment has a typo in the default Pico SDK path (`pick-sdk`). It requires relatively recent CMake 3.24.

Test signals: A successful Pico W build, serial/USB output showing Wi-Fi connection, and a remote SMB directory listing from the configured `SMB2_URL` validate the integration.
