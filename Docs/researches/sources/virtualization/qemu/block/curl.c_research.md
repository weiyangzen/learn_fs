# File Research: sources/virtualization/qemu/block/curl.c

Implements read-only HTTP, HTTPS, FTP, and FTPS protocol block drivers using libcurl multi/socket integration. It supports URL, readahead, SSL verification, timeout, cookies or cookie secret, username/password secret, proxy credentials, and force-range options.

`BDRVCURLState` owns the libcurl multi handle, timer, known length, up to eight `CURLState` transfer slots, socket table, URL/options, AioContext, mutex, free-state queue, and credentials. Each `CURLState` has an easy handle, cached read buffer, range string, error buffer, in-use flag, and waiting request slots. The code restricts allowed protocols to HTTP/HTTPS/FTP/FTPS, with separate handling for libcurl 7.85 string protocol APIs.

Open enforces read-only, initializes libcurl globally, parses options, validates readahead alignment and timeout, resolves secrets, verifies URL scheme matches the driver, initializes a curl state, performs a HEAD or forced `0-0` GET to determine size and byte-range support, rejects unknown size or HTTP(S) without range support, then attaches the multi handle to the BDS AioContext. Read requests first search cached/readahead buffers, can wait on overlapping active transfers, otherwise allocate a transfer state, allocate a readahead buffer, set a byte range, add the easy handle to the multi handle, kick curl, and yield until completion.

Completion handlers copy data into waiting qiovs, zero-fill beyond EOF, wake coroutines, and clean the transfer state. Aio attach/detach configures socket handlers and timers, cleans easy handles and buffers, and handles context migration. Four `BlockDriver`s register the same implementation under `http`, `https`, `ftp`, and `ftps`.
