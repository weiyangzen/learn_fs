# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/att20c49x.c

`att20c49x.c` is a RAMDAC module for ATT20C490/491/492 true-color CMOS RAMDACs. It validates requested pixel clock against a speed grade parsed from the controller name suffix, defaulting to 55 MHz.

`load` can put 20C491-class chips to sleep, then writes control register 0 to select mode and wake the chip. 8-bit color expansion logic is present but disabled with `&& 0`.

It exports three controller descriptors: `att20c490`, `att20c491`, and `att20c492`.
