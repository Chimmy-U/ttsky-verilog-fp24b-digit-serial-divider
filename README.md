![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg) [![Universidad del Quindío](https://img.shields.io/badge/Universidad-del%20Quindío-green)](https://www.uniquindio.edu.co/)

# IEEE | Tiny Tapeout Verilog 24-Bit Serial Fixed-Point Binary Divider

Serial divider implemented in Verilog for 24-bit fixed-point numbers with 23 fractional bits. Capable of performing normalized binary divisions within an approximate range of 0 to 1.9999999. Designed for [Tiny Tapeout](https://tinytapeout.com) SKY130.

*Design proposed by the University of Quindío.*

## Documentation

[Read the project documentation.](docs/info.md) It covers:
- Project description  
- How does it work?  
- How to test it?  

## Tiny Tapeout Details

| Property | Value |
|---|---|
| Top module | `tt_um_digit_serial_divider` |
| Tiles | 1x1 |
| Clock | 50 MHz (20 ns period) |
| Process | SKY130 |
| Language | Verilog |

### Pinout

#### Inputs (`ui_in`)

| Pin | Function |
|---|---|
| `ui_in[0]` | X (Serial bit input) |
| `ui_in[1]` | Y (Serial bit input) |
| `ui_in[2]` | START (Start signal) |
| `ui_in[7:3]` | Unused |

#### Outputs (`uo_out`)

| Pin | Function |
|---|---|
| `uo_out[0]` | Q (Quotient bit output) |
| `uo_out[1]` | DONE (Indicates operation complete) |
| `uo_out[7:2]` | Unused |

## What is Tiny Tapeout?

Tiny Tapeout is an educational project aimed at making it easier and more affordable than ever to manufacture your digital and analog designs on a real chip.

To learn more and get started, visit https://tinytapeout.com.

## Resources

- [FAQ](https://tinytapeout.com/faq/)
- [Digital design lessons](https://tinytapeout.com/digital_design/)
- [Learn how semiconductors work](https://tinytapeout.com/siliwiz/)
- [Join the community](https://tinytapeout.com/discord)
- [Build your design locally](https://www.tinytapeout.com/guides/local-hardening/)

### Social Media

- LinkedIn [#tinytapeout](https://www.linkedin.com/search/results/content/?keywords=%23tinytapeout) [@TinyTapeout](https://www.linkedin.com/company/100708654/)
- Mastodon [#tinytapeout](https://chaos.social/tags/tinytapeout) [@matthewvenn](https://chaos.social/@matthewvenn)
- X (formerly Twitter) [#tinytapeout](https://twitter.com/hashtag/tinytapeout) [@tinytapeout](https://twitter.com/tinytapeout)
- Bluesky [@tinytapeout.com](https://bsky.app/profile/tinytapeout.com)
