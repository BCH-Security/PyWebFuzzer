# Web Fuzzer – Hidden Endpoint Discovery Tool

A multi-threaded web fuzzing tool written in Python designed to discover hidden endpoints such as directories and files by sending HTTP requests using a wordlist.

This project demonstrates practical concepts used in penetration testing and web application reconnaissance.

---

## Disclaimer

This tool is intended strictly for:

- Educational purposes  
- Authorized security testing  
- Lab environments / CTF challenges  

Do **not** use this tool on systems you do not own or have explicit permission to test.

---

## Features

- Multi-threaded fuzzing for performance
- Supports HTTP and HTTPS
- Directory and file fuzzing modes
- Wordlist-based endpoint discovery
- Proxy support
- Custom HTTP headers
- Response filtering (status code & content length)
- Execution time estimation
- Output logging to file
- Graceful interruption (Ctrl+C handling)

---

## Requirements

- Python 3.x

No external libraries required (uses standard Python modules).

---

## Usage

### Basic Syntax

```bash
python3 web_fuzzer.py -u <URL> -m <mode> -w <wordlist>
```

## Modes
1. Directory Fuzzing
```bash
python3 web_fuzzer.py -u https://example.com -m fuzz_directories -w wordlist.txt
```

2. File Fuzzing
```bash
python3 web_fuzzer.py -u https://example.com -m fuzz_files -w wordlist.txt
```

## Options
| Option            | Description                                      |
| ----------------- | ------------------------------------------------ |
| `-u`              | Target URL                                       |
| `-m`              | Fuzz method (`fuzz_directories` or `fuzz_files`) |
| `-t`              | Number of threads (default: 10)                  |
| `-w`              | Wordlist file                                    |
| `-o`              | Output file                                      |
| `-r`              | Delay between requests                           |
| `-c`              | Connection timeout                               |
| `-x`              | Exclude status codes (e.g. 404,403)              |
| `-l`              | Exclude content lengths                          |
| `-H`              | Custom HTTP headers                              |
| `-p`              | HTTP proxy (IP:PORT)                             |
| `--enable-errors` | Show exceptions                                  |


## Example
```bash
python3 web_fuzzer.py \
-u https://target.com \
-m fuzz_directories \
-w common_dirs.txt \
-t 20 \
-x 404 \
-r 0.2
```

## Output Example
```bash
Response-Status-Code: 200 | Content-Length: 1024 | Header-Length: 512 | Response-Time(seconds): 0.3421 | Redirect-To:  | FUZZ-Value: admin
Response-Status-Code: 301 | Content-Length: 0    | Header-Length: 210 | Response-Time(seconds): 0.1203 | Redirect-To: /login | FUZZ-Value: dashboard
```

## Defensive Perspective

To protect against fuzzing attacks:

- Implement rate limiting
- Use Web Application Firewalls (WAF)
- Monitor logs for abnormal request patterns
- Disable directory listing
- Use authentication for sensitive endpoints



