# sources/user-network-fs/libsmb2/examples/picow/main.cpp

Purpose: This Pico W example connects to Wi-Fi under FreeRTOS, initializes libsmb2, connects to an SMB share, and lists a directory synchronously.

Important APIs and types: It uses Pico APIs `cyw43_arch_init`, `cyw43_arch_enable_sta_mode`, `cyw43_arch_wifi_connect_timeout_ms`, `stdio_init_all`, FreeRTOS `xTaskCreate`, `vTaskStartScheduler`, `vTaskDelete`, and libsmb2 APIs `smb2_init_context`, `smb2_parse_url`, `smb2_set_security_mode`, `smb2_connect_share`, `smb2_opendir`, `smb2_readdir`, `smb2_readlink`, `smb2_closedir`, and cleanup functions.

Control flow: `main` starts a FreeRTOS task. The task initializes Wi-Fi, connects with compile-time SSID/password, logs the assigned IPv4 address, then calls `smb2_ls_sync`. The listing function parses the compile-time SMB URL, connects, iterates directory entries, prints type and size, optionally resolves symlink targets, and destroys all SMB resources.

State and persistence behavior: Persistent configuration is compiled into the binary through CMake definitions. Runtime state includes the Wi-Fi connection, IP address, libsmb2 context, parsed URL, directory handle, and stack buffers for symlink paths.

Dependencies and integration points: It depends on the Pico W CYW43 Wi-Fi stack, lwIP in `NO_SYS=0` mode, FreeRTOS scheduling, and libsmb2's synchronous API working in an embedded environment.

Risks: Error paths call `exit`, which is not always appropriate for embedded firmware. The symlink path uses `sprintf` into a fixed 1024-byte buffer and the readlink target uses 256 bytes. The FreeRTOS task uses `configMINIMAL_STACK_SIZE`, which may be tight for SMB parsing and printing.

Test signals: Serial output should show Wi-Fi connection details, directory entries, symlink targets if present, and no scheduler crash. Testing long paths and authentication failures would exercise the risky branches.
