#!/usr/bin/python3

R = "\033[1;31m"
Y = "\033[1;33m"
C = "\033[1;36m"
W = "\033[0m"

import argparse
import http.client
from urllib.parse import quote, urlparse
import ssl
import time
import queue
import threading
import signal
import sys
import math

def signal_handler(signum, frame):
    global exit_flag
    print("Ctrl+C received. Stopping threads...")
    exit_flag = True


def GET_HTTP_Request(fuzz_method, wordlist, output_file, url_scheme, url_host, url_path, http_headers, request_delay, connection_timeout, execlude_list, execlude_length_list, http_proxy, queue_total_size):

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    while not q.empty():
        try:
            fuzz_value = q.get()

            if url_path[-1] == '/':
                new_path = url_path + quote(fuzz_value)
            else:
                new_path = url_path + '/' + quote(fuzz_value)

            if fuzz_method == 'fuzz_directories':
                new_path += '/'

            start_time = time.perf_counter()

            if url_scheme == 'http' and len(http_proxy) > 0:
                connection = http.client.HTTPConnection(http_proxy[0], int(http_proxy[1]), timeout=float(connection_timeout))
                connection.set_tunnel(url_host, 80)

            elif url_scheme == 'https' and len(http_proxy) > 0:
                connection = http.client.HTTPSConnection(http_proxy[0], int(http_proxy[1]), timeout=float(connection_timeout), context=context)
                connection.set_tunnel(url_host, 443)

            elif url_scheme == 'http' and len(http_proxy) == 0:
                connection = http.client.HTTPConnection(url_host, timeout=float(connection_timeout))

            elif url_scheme == 'https' and len(http_proxy) == 0:
                connection = http.client.HTTPSConnection(url_host, timeout=float(connection_timeout), context=context)

            else:
                print(f"{R}Error: {Y}Unsupported Scheme or Proxy{W}")
                exit(-1)

            connection.request('GET', new_path, headers=http_headers)
            response = connection.getresponse()

            if 'Content-Length' in response.headers:
                content_length = int(response.headers['Content-Length'])
            else:
                content_length = len(response.read().decode())

            if str(response.status) not in execlude_list and str(content_length) not in execlude_length_list:
                end_time = time.perf_counter()
                elapsed_time = round(end_time - start_time, 4)

                headers = response.getheaders()
                headers_str = '\r\n'.join([f"{name}: {value}" for name, value in headers]) + '\r\n\r\n'
                headers_length = len(headers_str)

                result = f"Response-Status-Code: {response.status:3} | Content-Length: {content_length:5} | Header-Length: {headers_length:5} | Response-Time(seconds): {str(elapsed_time):6} | Redirect-To: {response.headers.get('location', '')} | FUZZ-Value: {fuzz_value}"

                print(result)

                with file_lock:
                    file_writer.write(result + "\n")

        except Exception as e:
            if display_errors:
                print(f"{R}Exception When Fuzzing {Y}{fuzz_value}: {R}{e}{W}")

        if exit_flag:
            with q.mutex:
                q.queue.clear()
                q.all_tasks_done.notify_all()
                q.unfinished_tasks = 0
            return

        q.task_done()
        event.wait(float(request_delay))
        print(f"\r[+] Queue Size: {str(round((q.qsize()/queue_total_size)*100,2)):5}%", end=' ')


def main(url, fuzz_method, num_threads, wordlist, output_file, request_delay, connection_timeout, execlude_list, execlude_length_list, headers, http_proxy):

    http_headers = {}
    for header in headers:
        key, value = header.split(':')
        http_headers[key] = value

    parsed_url = urlparse(url)
    url_scheme = parsed_url.scheme
    url_host = parsed_url.netloc
    url_path = parsed_url.path

    with open(wordlist) as wordlist_items:
        for wordlist_item in wordlist_items:
            q.put(wordlist_item.strip())

    queue_total_size = q.qsize()

    total_time = math.ceil((queue_total_size / num_threads) * float(request_delay))
    hours = total_time // 3600
    minutes = (total_time % 3600) // 60
    remaining_seconds = total_time % 60

    print("Number of items:", queue_total_size)
    print(f"Expected Time: {hours}h:{minutes}m:{remaining_seconds}s")

    for _ in range(num_threads):
        threading.Thread(
            target=GET_HTTP_Request,
            args=(fuzz_method, wordlist, output_file, url_scheme, url_host, url_path, http_headers, request_delay, connection_timeout, execlude_list, execlude_length_list, http_proxy, queue_total_size)
        ).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Fuzzer")

    parser.add_argument("--enable-errors", action="store_true")
    parser.add_argument("-u", "--url")
    parser.add_argument("-m", "--fuzz-method")
    parser.add_argument("-t", "--num-threads", type=int, default=10)
    parser.add_argument("-w", "--wordlist")
    parser.add_argument("-o", "--output-file", default="Fuzz_results.txt")
    parser.add_argument("-r", "--request-delay", default='0.300')
    parser.add_argument("-c", "--connection-timeout", default=10)
    parser.add_argument("-x", "--execlude-status-code")
    parser.add_argument("-l", "--execlude-length")

    parser.add_argument('-H', '--headers', metavar='Header:Value', nargs='*', action='append', default=[["User-Agent:Mozilla/5.0"]])
    parser.add_argument("-p", "--http-proxy")

    args = parser.parse_args()

    display_errors = args.enable_errors
    url = args.url
    fuzz_method = args.fuzz_method
    num_threads = args.num_threads
    wordlist = args.wordlist
    output_file = args.output_file
    request_delay = args.request_delay
    connection_timeout = args.connection_timeout

    execlude_list = args.execlude_status_code.split(",") if args.execlude_status_code else []
    execlude_length_list = args.execlude_length.split(",") if args.execlude_length else []

    headers = [item for sublist in args.headers for item in sublist]
    http_proxy = args.http_proxy.split(":") if args.http_proxy else []

    exit_flag = False
    signal.signal(signal.SIGINT, signal_handler)

    event = threading.Event()
    q = queue.Queue()

    file_lock = threading.Lock()
    file_writer = open(output_file, "wt", 1)

    T1 = time.perf_counter()

    main(url, fuzz_method, num_threads, wordlist, output_file, request_delay, connection_timeout, execlude_list, execlude_length_list, headers, http_proxy)

    q.join()

    T2 = time.perf_counter()
    total = T2 - T1

    print(f"\nDone in {total:.2f} seconds")