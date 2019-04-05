import json  
import subprocess  
import logging

# standard logging
logger = logging.getLogger(__name__)

def stream_curl(url):  
    process = subprocess.Popen(['/usr/bin/curl', '-H', 'X-API-Key: F5C4CB3814AB4148B2C4DAF6AC3DA50D', url], stdout=subprocess.PIPE)

    ix = 0
    empty_lines = 0
    while True:
        line = process.stdout.readline()
        print(line['eventType'])

        # process ended
        if process.poll() is not None:
            logger.info('Downloading completed after %s lines.', ix)
            break

        ix += 1
        if not line:
            logger.warning('Empty line: `%s`!', ix)
            if empty_lines > 10:
                raise IOError('To many empty lines when downloading data!')
            empty_lines += 1
        else:
            yield json.loads(line)

my_stream = stream_curl('https://partners.dnaspaces.io/api/partners/v1/firehose/events')  
for json_object in my_stream:  
    print(json_object)