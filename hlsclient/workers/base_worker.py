import logging
import signal
import sys
import time

from lockfile import LockTimeout

from hlsclient import helpers
from hlsclient.lock import ExpiringLinkLockFile


class Worker(object):
    def __init__(self):
        self.config = helpers.load_config()
        self.setup_lock()

    def setup(self):
        pass

    def lock_path(self):
        return self.config.get('lock', 'path')

    def run(self):
        raise NotImplementedError()

    def lost_lock_callback(self):
        pass

    def should_run(self):
        return True

    def interrupted(self, *args):
        logging.info('Interrupted. Releasing lock.')
        self.stop()

    def setup_lock(self):
        lock_path = self.lock_path()
        self.lock_timeout = self.config.getint('lock', 'timeout')
        self.lock_expiration = self.config.getint('lock', 'expiration')
        self.lock = ExpiringLinkLockFile(lock_path)

    def run_forever(self):
        self.setup()
        signal.signal(signal.SIGTERM, self.interrupted)
        while self.should_run():
            try:
                self.run_if_locking()
            except LockTimeout:
                logging.debug("Unable to acquire lock")
            except Exception as e:
                logging.exception('An unknown error happened')
            except KeyboardInterrupt:
                logging.debug('Quitting...')
                break
            time.sleep(0.1)
        self.stop()

    def run_if_locking(self):
        if self.can_run():
            self.lock.update_lock()
            self.run()

    def can_run(self):
        if self.other_is_running():
            logging.warning("Someone else acquired the lock")
            self.lost_lock_callback()
        elif not self.lock.is_locked():
            self.lock.acquire(timeout=self.lock_timeout)
        return self.lock.i_am_locking()

    def other_is_running(self):
        other = self.lock.is_locked() and not self.lock.i_am_locking()
        if other and self.lock.expired(tolerance=self.lock_expiration):
            logging.warning("Lock expired. Breaking it")
            self.lock.break_lock()
            return False
        return other

    def stop(self):
        try:
            self.lock.release_if_locking()
        finally:
            sys.exit(0)