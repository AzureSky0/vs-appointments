"""Run the VS Appointments end-to-end tests in a headless browser.

    python tests/run_tests.py                    # the app in this repository (with offline checks)
    set VS_TEST_VERBOSE=1                        # (Windows) print every check as it runs

Serves this repository on http://localhost, opens tests/tests.html in headless Edge (or Chrome),
and waits for the page to post its results back. Exits 1 if anything failed.

The browser is found automatically on Windows. Elsewhere, point VS_TEST_BROWSER at a Chrome,
Chromium or Edge executable.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
PORT = 8765
VERBOSE = bool(os.environ.get('VS_TEST_VERBOSE'))
TIMEOUT = int(os.environ.get('VS_TEST_TIMEOUT', 240))
BROWSERS = [
    os.environ.get('VS_TEST_BROWSER', ''),
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    shutil.which('msedge') or '', shutil.which('google-chrome') or '', shutil.which('chromium') or '',
]

done = threading.Event()
report = {}
# The offline tests ask the server to pretend the site is down or the network is slow.
mode = {'value': 'normal'}


class Handler(SimpleHTTPRequestHandler):
    # Windows' registry maps .js to text/plain; browsers refuse service workers served like that.
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, '.js': 'text/javascript',
                      '.webmanifest': 'application/manifest+json'}

    def do_POST(self):
        if self.path == '/__results':
            report.update(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
            self.send_response(204)
            self.end_headers()
            done.set()

    def do_GET(self):
        if self.path.startswith('/__log?'):
            print('  ..', unquote(self.path[7:]), flush=True)
            return self._no_content()
        if self.path.startswith('/__mode?'):
            mode['value'] = self.path[8:]
            return self._no_content()
        if not self.path.startswith('/tests/'):
            if mode['value'] == 'down':
                self.send_response(404)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>404 Site not found</h1>')
                return
            if mode['value'] == 'slow':
                time.sleep(10)
        super().do_GET()

    def _no_content(self):
        self.send_response(204)
        self.end_headers()

    def log_message(self, *args):
        pass


def find_browser():
    for path in BROWSERS:
        if path and Path(path).exists():
            return path
    sys.exit('No browser found. Set VS_TEST_BROWSER to the path of Chrome, Chromium or Edge.')


def run(browser):
    url = f'http://localhost:{PORT}/tests/tests.html?app=/index.html&pwa=1&modes=1' + ('&verbose=1' if VERBOSE else '')
    profile = tempfile.mkdtemp(prefix='vs-tests-')
    args = [browser, '--headless=new', '--disable-gpu', f'--user-data-dir={profile}',
            '--window-size=900,900', '--no-first-run']
    if sys.platform.startswith('linux'):
        args.append('--no-sandbox')
    proc = subprocess.Popen(args + [url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        finished = done.wait(TIMEOUT)
    finally:
        proc.kill()
        proc.wait()
        shutil.rmtree(profile, ignore_errors=True)
    if not finished:
        print('TIMEOUT: no results from the test page')
        return False
    print(f'\n=== {report["total"] - report["failed"]}/{report["total"]} passed ===')
    for r in report['results']:
        if not r['ok']:
            print(f'  FAIL  {r["name"]}  ->  {r["detail"]}')
    return report['failed'] == 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    server = ThreadingHTTPServer(('127.0.0.1', PORT), partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    ok = run(find_browser())
    server.shutdown()
    print('\nALL PASSED' if ok else '\nSOME TESTS FAILED')
    sys.exit(0 if ok else 1)
