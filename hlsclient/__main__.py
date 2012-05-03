import ConfigParser
import logging
import time

from balancer import Balancer
from discover import discover
from consumer import consume

def load_config(path='config.ini'):
    config = ConfigParser.RawConfigParser()
    with open(path) as f:
        config.readfp(f)
    return config

def main():
    logging.basicConfig()
    logger = logging.getLogger('hls-client')
    logger.setLevel(logging.DEBUG)
    logger.debug('HLS CLIENT Started')

    config = load_config()
    destination = config.get('hlsclient', 'destination')
    logger.debug('Config loaded')

    balancer = Balancer()

    while True:
        paths = discover(config)
        logger.info(u'Discovered the following paths: %s' % paths.items())
        balancer.update(paths)

        for resource in balancer.actives:
            resource_path = str(resource)
            logger.debug('Consuming %s' % resource_path)
            try:
                modified = consume(resource_path, destination)
            except (IOError, OSError) as err:
                logger.warning(u'Notifying error for resource %s: %s' % (resource_path, err))
                balancer.notify_error(resource.server, resource.path)
            else:
                if modified:
                    logger.info('Notifying content modifed: %s' % resource)
                    balancer.notify_modified(resource.server, resource.path)
                else:
                    logger.debug('Content not modified: %s' % resource)
        time.sleep(2)

if __name__ == "__main__":
    main()